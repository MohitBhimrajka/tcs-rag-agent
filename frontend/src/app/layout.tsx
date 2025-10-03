// frontend/src/app/layout.tsx
import './globals.css'

export const metadata = {
  title: 'Financial Extraction Agent',
  description: 'Extract structured data from annual reports using an AI agent.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  )
}