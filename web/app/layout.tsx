import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI+OR Daily Report",
  description: "每日 AI + 运筹优化前沿论文精选",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        {/* Header */}
        <header className="bg-gradient-to-r from-blue-900 via-blue-800 to-purple-900 text-white shadow-lg">
          <div className="max-w-5xl mx-auto px-4 py-6">
            <div className="flex items-center gap-3">
              <span className="text-4xl">🔬</span>
              <div>
                <h1 className="text-2xl font-bold tracking-tight">AI+OR Daily Report</h1>
                <p className="text-blue-200 text-sm mt-0.5">
                  每日精选 · 运筹优化 × 人工智能前沿论文
                </p>
              </div>
            </div>
            <div className="flex gap-4 mt-4 text-xs text-blue-300">
              <span>🤗 HuggingFace</span>
              <span>·</span>
              <span>📄 arXiv</span>
              <span>·</span>
              <span>💻 PapersWithCode</span>
              <span>·</span>
              <span>🤖 Powered by DeepSeek</span>
            </div>
          </div>
        </header>

        <main className="max-w-5xl mx-auto px-4 py-8">{children}</main>

        <footer className="border-t bg-white text-center py-5 text-gray-400 text-sm mt-12">
          <p>
            Built with ❤️ ·{" "}
            <a
              href="https://github.com/bujibujibiuwang/daily_AIOR_report"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline"
            >
              GitHub
            </a>
          </p>
        </footer>
      </body>
    </html>
  );
}
