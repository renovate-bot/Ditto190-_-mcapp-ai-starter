import { useState } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { CodespaceStatus } from '@/pages/CodespaceStatus'
import { Services } from '@/pages/Services'

type Page = 'status' | 'services'

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('status')

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {currentPage === 'status' && <CodespaceStatus />}
          {currentPage === 'services' && <Services />}
        </main>
      </div>
    </div>
  )
}
