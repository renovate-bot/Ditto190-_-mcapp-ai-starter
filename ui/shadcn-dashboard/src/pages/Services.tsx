import { Server } from 'lucide-react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

/**
 * Services page — stub / placeholder.
 *
 * TODO(future-agent): Build out this page with:
 *   - Per-service log viewer (stream docker logs via SSE or WebSocket)
 *   - Start/stop/restart buttons per service
 *   - Docker Compose config display
 *
 * Pattern references:
 *   - shadcn-admin features: https://github.com/Ditto190/shadcn-admin/tree/main/src/features
 *   - shadcn-vue-modme (Vue equivalent): https://github.com/Ditto190/shadcn-vue-modme
 */
export function Services() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Services</h1>
        <p className="text-sm text-muted-foreground">
          Docker Compose service management — coming soon.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm flex items-center gap-2">
            <Server className="h-4 w-4" />
            Coming Soon
          </CardTitle>
          <CardDescription>
            This page is a placeholder for future service-management features.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Badge variant="outline">Not implemented</Badge>
          <ul className="text-sm text-muted-foreground list-disc list-inside space-y-1">
            <li>Per-service start / stop / restart controls</li>
            <li>Live log streaming (docker logs via SSE)</li>
            <li>Container resource usage (CPU, memory per container)</li>
            <li>Docker Compose file viewer</li>
          </ul>
          <p className="text-xs text-muted-foreground pt-2 border-t">
            See <code className="bg-muted px-1 rounded">docs/shadcn-dashboard-foundation.md</code> for
            the next-steps roadmap.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
