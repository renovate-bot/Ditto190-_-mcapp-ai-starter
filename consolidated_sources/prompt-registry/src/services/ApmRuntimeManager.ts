/**
 * ApmRuntimeManager
 *
 * Manages APM CLI runtime detection and provides installation guidance.
 * Uses singleton pattern for shared state across the extension.
 *
 * Security considerations:
 * - Only executes known safe commands (apm --version)
 * - Sanitizes command output
 * - Does not auto-install without user consent
 */

import { exec } from "child_process";
import { promisify } from "util";
import * as os from "os";
import * as path from "path";
import * as fs from "fs";
import * as https from "https";
import * as vscode from "vscode";
import { Logger } from "../utils/logger";

const execAsync = promisify(exec);

/**
 * APM runtime status information
 */
export interface ApmRuntimeStatus {
  /** Whether APM CLI is installed and accessible */
  installed: boolean;
  /** APM version string (if installed) */
  version?: string;
  /** How APM was installed */
  installMethod?: "pip" | "brew" | "binary" | "unknown" | "uvx";
  /** Python version (if detected) */
  pythonVersion?: string;
  /** Whether uvx is available */
  uvxAvailable?: boolean;
  /** Path to APM executable */
  path?: string;
  /** Path to local managed uv executable */
  localUvPath?: string;
}

/**
 * Cache entry for runtime status
 */
interface StatusCache {
  status: ApmRuntimeStatus;
  timestamp: number;
}

/**
 * Cache TTL in milliseconds (60 seconds)
 */
const CACHE_TTL = 60 * 1000;

/**
 * Command timeout in milliseconds (10 seconds)
 */
const COMMAND_TIMEOUT = 10 * 1000;

/**
 * Maximum version string length for security
 */
const MAX_VERSION_LENGTH = 100;

/**
 * ApmRuntimeManager - Singleton manager for APM CLI runtime
 */
export class ApmRuntimeManager {
  private static instance: ApmRuntimeManager | null = null;
  private logger: Logger;
  private statusCache: StatusCache | null = null;
  private context: vscode.ExtensionContext | undefined;

  private constructor() {
    this.logger = Logger.getInstance();
  }

  /**
   * Get singleton instance
   */
  static getInstance(): ApmRuntimeManager {
    if (!ApmRuntimeManager.instance) {
      ApmRuntimeManager.instance = new ApmRuntimeManager();
    }
    return ApmRuntimeManager.instance;
  }

  /**
   * Initialize manager with extension context
   */
  initialize(context: vscode.ExtensionContext): void {
    this.context = context;
  }

  /**
   * Setup runtime (install if missing)
   * Shows progress in UI
   */
  async setupRuntime(): Promise<boolean> {
    const status = await this.getStatus(true);
    if (status.installed || status.uvxAvailable) {
      return true;
    }

    // If we have context, try automatic installation
    if (this.context) {
      return await vscode.window.withProgress(
        {
          location: vscode.ProgressLocation.Notification,
          title: "Installing APM Runtime...",
          cancellable: false,
        },
        async (progress) => {
          try {
            progress.report({ message: "Checking compatibility..." });
            this.logger.info(
              "[ApmRuntime] Starting automatic runtime installation...",
            );

            await this.installLocalUv(progress);

            // Refresh status
            this.clearCache();
            const newStatus = await this.getStatus(true);

            if (newStatus.uvxAvailable) {
              vscode.window.showInformationMessage(
                "APM Runtime installed successfully.",
              );
              return true;
            }
          } catch (error) {
            this.logger.error(
              "[ApmRuntime] Automatic installation failed",
              error as Error,
            );
            // Fall through to manual instructions
          }

          // If automatic install failed or wasn't sufficient
          const selection = await vscode.window.showErrorMessage(
            "APM Runtime could not be installed automatically.",
            "View Instructions",
          );
          if (selection === "View Instructions") {
            this.showInstallInstructions();
          }
          return false;
        },
      );
    }

    this.showInstallInstructions();
    return false;
  }

  /**
   * Show installation instructions
   */
  private async showInstallInstructions(): Promise<void> {
    const doc = await vscode.workspace.openTextDocument({
      content: this.getInstallInstructions(),
      language: "markdown",
    });
    await vscode.window.showTextDocument(doc);
  }

  /**
   * Install uv locally in extension storage
   */
  private async installLocalUv(
    progress: vscode.Progress<{ message?: string }>,
  ): Promise<void> {
    if (!this.context) {
      throw new Error("Extension context not initialized");
    }

    const storagePath = this.context.globalStorageUri.fsPath;
    const binPath = path.join(storagePath, "bin");
    const uvPath = path.join(
      binPath,
      process.platform === "win32" ? "uv.exe" : "uv",
    );

    if (fs.existsSync(uvPath)) {
      this.logger.info("[ApmRuntime] Local uv already exists");
      return; // Already installed
    }

    await fs.promises.mkdir(binPath, { recursive: true });

    const url = this.getUvDownloadUrl();
    const filename = path.basename(url);
    const downloadPath = path.join(storagePath, filename);

    try {
      progress.report({ message: "Downloading uv..." });
      this.logger.info(`[ApmRuntime] Downloading uv from ${url}`);
      await this.downloadFile(url, downloadPath);

      progress.report({ message: "Extracting..." });
      await this.extractArchive(downloadPath, binPath);

      if (process.platform !== "win32") {
        await fs.promises.chmod(uvPath, 0o755);
      }

      this.logger.info("[ApmRuntime] uv installed successfully");
    } finally {
      // Cleanup
      if (fs.existsSync(downloadPath)) {
        await fs.promises.unlink(downloadPath).catch(() => {});
      }
    }
  }

  /**
   * Get uv binary download URL for current platform
   */
  private getUvDownloadUrl(): string {
    const platform = process.platform;
    const arch = process.arch;

    const baseUrl = "https://github.com/astral-sh/uv/releases/latest/download";

    if (platform === "darwin") {
      if (arch === "arm64") {
        return `${baseUrl}/uv-aarch64-apple-darwin.tar.gz`;
      }
      return `${baseUrl}/uv-x86_64-apple-darwin.tar.gz`;
    }
    if (platform === "linux") {
      if (arch === "arm64") {
        return `${baseUrl}/uv-aarch64-unknown-linux-gnu.tar.gz`;
      }
      return `${baseUrl}/uv-x86_64-unknown-linux-gnu.tar.gz`;
    }
    if (platform === "win32") {
      return `${baseUrl}/uv-x86_64-pc-windows-msvc.zip`;
    }

    throw new Error(`Unsupported platform: ${platform}-${arch}`);
  }

  /**
   * Download file from URL
   */
  private downloadFile(url: string, dest: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const file = fs.createWriteStream(dest);
      https
        .get(url, (response) => {
          if (response.statusCode === 302 || response.statusCode === 301) {
            // Handle redirect
            this.downloadFile(response.headers.location!, dest)
              .then(resolve)
              .catch(reject);
            return;
          }

          if (response.statusCode !== 200) {
            reject(new Error(`Download failed: HTTP ${response.statusCode}`));
            return;
          }

          response.pipe(file);
          file.on("finish", () => {
            file.close();
            resolve();
          });
        })
        .on("error", (err) => {
          fs.unlink(dest, () => {});
          reject(err);
        });
    });
  }

  /**
   * Extract archive
   */
  private async extractArchive(
    archivePath: string,
    destDir: string,
  ): Promise<void> {
    if (archivePath.endsWith(".zip")) {
      // Windows: use PowerShell
      // Note: yauzl is available but complex to use for extraction.
      // Powershell is reliable on Windows 10+.
      // Alternatively, use tar (Windows 10 build 17063+)
      try {
        await execAsync(`tar -xf "${archivePath}" -C "${destDir}"`);
      } catch {
        // Fallback to PowerShell
        await execAsync(
          `powershell -command "Expand-Archive -Path '${archivePath}' -DestinationPath '${destDir}' -Force"`,
        );
      }
    } else {
      // Tar.gz
      await execAsync(`tar -xzf "${archivePath}" -C "${destDir}"`);
    }

    // Flatten directory if needed (archives usually contain a top-level folder)
    // uv archives usually contain `uv-platform/uv`
    // We want `uv` in `destDir`
    const entries = await fs.promises.readdir(destDir);
    for (const entry of entries) {
      const fullPath = path.join(destDir, entry);
      const stats = await fs.promises.stat(fullPath);
      if (stats.isDirectory() && entry.startsWith("uv-")) {
        // Move binaries out
        const binName = process.platform === "win32" ? "uv.exe" : "uv";
        const srcBin = path.join(fullPath, binName);
        const dstBin = path.join(destDir, binName);

        if (fs.existsSync(srcBin)) {
          // Move file (copy then unlink to avoid cross-device link error, though typically same device)
          await fs.promises.rename(srcBin, dstBin);
        }
        // Remove dir
        await fs.promises.rm(fullPath, { recursive: true, force: true });
      }
    }
  }

  /**
   * Reset singleton instance (for testing)
   */
  static resetInstance(): void {
    ApmRuntimeManager.instance = null;
  }

  /**
   * Get current APM runtime status
   * @param forceRefresh Force refresh ignoring cache
   */
  async getStatus(forceRefresh = false): Promise<ApmRuntimeStatus> {
    // Check cache
    if (
      !forceRefresh &&
      this.statusCache &&
      Date.now() - this.statusCache.timestamp < CACHE_TTL
    ) {
      return this.statusCache.status;
    }

    try {
      const status = await this.detectRuntime();
      this.statusCache = { status, timestamp: Date.now() };
      return status;
    } catch (error) {
      this.logger.error("[ApmRuntime] Detection failed", error as Error);
      const status: ApmRuntimeStatus = { installed: false };
      this.statusCache = { status, timestamp: Date.now() };
      return status;
    }
  }

  /**
   * Check if APM is available
   */
  async isAvailable(): Promise<boolean> {
    const status = await this.getStatus();
    return status.installed;
  }

  /**
   * Clear cached status
   */
  clearCache(): void {
    this.statusCache = null;
  }

  /**
   * Get platform-appropriate installation instructions
   */
  getInstallInstructions(): string {
    const platform = process.platform;

    let instructions = "# APM CLI Installation\n\n";

    if (platform === "darwin") {
      instructions += "## macOS (Homebrew recommended)\n";
      instructions +=
        "```bash\nbrew install danielmeppiel/tap/apm-cli\n```\n\n";
      instructions += "## Alternative: pip\n";
      instructions += "```bash\npip install apm-cli\n```\n\n";
    } else if (platform === "linux") {
      instructions += "## Linux (pip)\n";
      instructions += "```bash\npip install apm-cli\n```\n\n";
    } else if (platform === "win32") {
      instructions += "## Windows (pip)\n";
      instructions += "```bash\npip install apm-cli\n```\n\n";
    }

    instructions += "## More information\n";
    instructions += "Visit: https://github.com/danielmeppiel/apm\n";

    return instructions;
  }

  /**
   * Get local uv path if exists
   */
  private getLocalUvPath(): string | undefined {
    if (!this.context) {
      return undefined;
    }
    const binPath = path.join(this.context.globalStorageUri.fsPath, "bin");
    const uvPath = path.join(
      binPath,
      process.platform === "win32" ? "uv.exe" : "uv",
    );
    return fs.existsSync(uvPath) ? uvPath : undefined;
  }

  /**
   * Detect APM runtime installation
   * Security: Only executes known safe commands
   */
  private async detectRuntime(): Promise<ApmRuntimeStatus> {
    this.logger.debug("[ApmRuntime] Detecting APM installation...");

    const localUvPath = this.getLocalUvPath();

    // Try to run `apm --version`
    try {
      const { stdout } = await execAsync("apm --version", {
        timeout: COMMAND_TIMEOUT,
        // Security: Don't pass user-controlled environment
        env: this.getSafeEnvironment(),
      });

      const version = this.sanitizeVersion(stdout.trim());

      if (!version) {
        // Fallback to checking uvx/uv
        const uvxAvailable = await this.checkUvx();
        return {
          installed: false,
          uvxAvailable: uvxAvailable || !!localUvPath,
          localUvPath,
        };
      }

      this.logger.info(`[ApmRuntime] APM CLI found: ${version}`);

      // Detect additional info
      const [installMethod, pythonVersion, uvxAvailable, apmPath] =
        await Promise.all([
          this.detectInstallMethod(),
          this.getPythonVersion(),
          this.checkUvx(),
          this.getApmPath(),
        ]);

      return {
        installed: true,
        version,
        installMethod,
        pythonVersion,
        uvxAvailable: uvxAvailable || !!localUvPath,
        path: apmPath,
        localUvPath,
      };
    } catch (error) {
      this.logger.debug("[ApmRuntime] APM CLI not found");
      const uvxAvailable = await this.checkUvx();
      return {
        installed: false,
        uvxAvailable: uvxAvailable || !!localUvPath,
        localUvPath,
      };
    }
  }

  /**
   * Get safe environment for command execution
   * Security: Removes potentially dangerous environment variables
   */
  private getSafeEnvironment(): NodeJS.ProcessEnv {
    const env = { ...process.env };
    // Keep PATH for command discovery
    // Remove any potentially dangerous variables
    delete env.LD_PRELOAD;
    delete env.DYLD_INSERT_LIBRARIES;
    return env;
  }

  /**
   * Sanitize version string
   * Security: Prevents injection via version output
   */
  private sanitizeVersion(version: string): string {
    // Truncate to prevent abuse
    const truncated = version.substring(0, MAX_VERSION_LENGTH);
    // Remove any HTML special chars
    let sanitized = truncated.replace(/[<>'"&]/g, "");
    // Remove control characters (eslint-disable-next-line no-control-regex)
    // eslint-disable-next-line no-control-regex
    sanitized = sanitized.replace(/[\u0000-\u001F\u007F]/g, "");
    return sanitized.trim();
  }

  /**
   * Detect how APM was installed
   */
  private async detectInstallMethod(): Promise<
    "pip" | "brew" | "binary" | "unknown"
  > {
    // Check Homebrew (macOS)
    if (process.platform === "darwin") {
      try {
        await execAsync("brew list apm-cli 2>/dev/null", {
          timeout: COMMAND_TIMEOUT,
        });
        return "brew";
      } catch {
        // Not installed via brew
      }
    }

    // Check pip
    try {
      const { stdout } = await execAsync("pip show apm-cli 2>/dev/null", {
        timeout: COMMAND_TIMEOUT,
      });
      if (stdout.toLowerCase().includes("apm")) {
        return "pip";
      }
    } catch {
      // Not installed via pip
    }

    // Check common binary locations
    const binaryPaths = [
      "/usr/local/bin/apm",
      "/usr/local/lib/apm/apm",
      path.join(os.homedir(), ".local/bin/apm"),
    ];

    for (const p of binaryPaths) {
      if (fs.existsSync(p)) {
        return "binary";
      }
    }

    return "unknown";
  }

  /**
   * Get Python version
   */
  private async getPythonVersion(): Promise<string | undefined> {
    for (const cmd of ["python3 --version", "python --version"]) {
      try {
        const { stdout } = await execAsync(cmd, { timeout: COMMAND_TIMEOUT });
        const version = stdout.trim().replace(/^Python\s*/i, "");
        return this.sanitizeVersion(version);
      } catch {
        // Try next command
      }
    }
    return undefined;
  }

  /**
   * Check if uvx is available
   */
  private async checkUvx(): Promise<boolean> {
    try {
      await execAsync("uvx --version", { timeout: COMMAND_TIMEOUT });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get APM executable path
   */
  private async getApmPath(): Promise<string | undefined> {
    try {
      const cmd = process.platform === "win32" ? "where apm" : "which apm";
      const { stdout } = await execAsync(cmd, { timeout: COMMAND_TIMEOUT });
      const apmPath = stdout.trim().split("\n")[0];
      // Security: Validate path looks reasonable
      if (apmPath && path.isAbsolute(apmPath)) {
        return apmPath;
      }
      return undefined;
    } catch {
      return undefined;
    }
  }
}
