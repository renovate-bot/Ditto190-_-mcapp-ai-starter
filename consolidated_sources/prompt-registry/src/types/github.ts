/**
 * GitHub release asset information
 */
export interface GitHubAsset {
  id: number;
  name: string;
  label: string | null;
  content_type: string;
  size: number;
  download_count: number;
  created_at: string;
  updated_at: string;
  browser_download_url: string;
}

/**
 * GitHub release information
 */
export interface GitHubRelease {
  id: number;
  tag_name: string;
  name: string;
  body: string;
  draft: boolean;
  prerelease: boolean;
  created_at: string;
  published_at: string;
  assets: GitHubAsset[];
  html_url: string;
  tarball_url: string;
  zipball_url: string;
}

/**
 * Parsed version information from release
 */
export interface VersionInfo {
  version: string;
  tagName?: string; // Original tag name from GitHub (e.g., "v1.0.0" or "1.0.0")
  major: number;
  minor: number;
  patch: number;
  prerelease?: string;
  isPrerelease: boolean;
}

/**
 * Platform-specific bundle information
 */
export interface BundleInfo {
  platform: string;
  version: string;
  asset: GitHubAsset;
  downloadUrl: string;
  filename: string;
  size: number;
}
