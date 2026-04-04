/**
 * Mock data and utilities for testing Prompt Registry bundle functionality
 */
export interface MockBundleAsset {
  id: number;
  name: string;
  browser_download_url: string;
  size: number;
  content_type: string;
}
export interface MockReleaseResponse {
  id: number;
  tag_name: string;
  name: string;
  published_at: string;
  assets: MockBundleAsset[];
}
/**
 * Mock GitHub release response simulating Prompt Registry bundle releases
 */
export declare const createMockReleaseResponse: (
  version?: string,
) => MockReleaseResponse;
/**
 * Load actual file content from test fixtures
 */
export declare const loadBundleContentFromFixtures: () => Record<
  string,
  Record<string, string>
>;
/**
 * Validate that a bundle contains expected platform-specific content
 */
export declare const validateBundleContent: (
  platform: string,
  files: Record<string, string>,
) => boolean;
/**
 * Create a temporary workspace directory for testing
 */
export declare const createTestWorkspace: () => string;
/**
 * Clean up test workspace
 */
export declare const cleanupTestWorkspace: (workspacePath: string) => void;
//# sourceMappingURL=mockData.d.ts.map
