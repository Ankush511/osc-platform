"use client"

import ReactMarkdown, { Components } from "react-markdown"
import remarkGfm from "remark-gfm"

interface MarkdownProps {
  content: string
  className?: string
}

const components: Components = {
  // Better code blocks with language label feel
  pre({ children }) {
    return (
      <pre className="bg-[#0d1117] border border-white/10 rounded-xl p-5 my-4 overflow-x-auto text-sm leading-relaxed">
        {children}
      </pre>
    )
  },
  code({ children, className }) {
    const isBlock = className?.startsWith("language-")
    if (isBlock) {
      return <code className={`${className} text-gray-300 font-mono text-[13px]`}>{children}</code>
    }
    return (
      <code className="text-cyan-300 bg-cyan-500/10 px-1.5 py-0.5 rounded-md text-[13px] font-mono">
        {children}
      </code>
    )
  },
  // Numbered list items with accent markers
  ol({ children }) {
    return <ol className="text-gray-300 my-4 space-y-2 list-decimal list-outside pl-5 marker:text-cyan-400 marker:font-semibold">{children}</ol>
  },
  ul({ children }) {
    return <ul className="text-gray-300 my-3 space-y-1.5 list-disc list-outside pl-5 marker:text-cyan-500/70">{children}</ul>
  },
  li({ children }) {
    return <li className="text-gray-300 leading-7 pl-1">{children}</li>
  },
  // Headings with subtle bottom border for visual separation
  h1({ children }) {
    return <h1 className="text-2xl font-black text-white mt-6 mb-3 pb-2 border-b border-white/5">{children}</h1>
  },
  h2({ children }) {
    return <h2 className="text-xl font-bold text-white mt-6 mb-3 pb-1.5 border-b border-white/5">{children}</h2>
  },
  h3({ children }) {
    return <h3 className="text-lg font-bold text-white mt-5 mb-2">{children}</h3>
  },
  h4({ children }) {
    return <h4 className="text-base font-semibold text-white mt-4 mb-2">{children}</h4>
  },
  p({ children }) {
    return <p className="text-gray-300 leading-7 mb-3">{children}</p>
  },
  a({ href, children }) {
    return (
      <a href={href} target="_blank" rel="noopener noreferrer"
        className="text-cyan-400 hover:text-cyan-300 underline decoration-cyan-500/30 hover:decoration-cyan-400/60 underline-offset-2 transition-colors">
        {children}
      </a>
    )
  },
  blockquote({ children }) {
    return (
      <blockquote className="border-l-2 border-cyan-500/40 text-gray-400 bg-white/[0.02] rounded-r-xl py-2 px-4 my-4 italic">
        {children}
      </blockquote>
    )
  },
  strong({ children }) {
    return <strong className="text-white font-semibold">{children}</strong>
  },
  hr() {
    return <hr className="border-white/10 my-6" />
  },
  table({ children }) {
    return (
      <div className="overflow-x-auto my-4 rounded-xl border border-white/10">
        <table className="w-full border-collapse">{children}</table>
      </div>
    )
  },
  th({ children }) {
    return <th className="border border-white/10 bg-white/5 px-4 py-2.5 text-left text-white font-bold text-sm">{children}</th>
  },
  td({ children }) {
    return <td className="border border-white/10 px-4 py-2.5 text-gray-400 text-sm">{children}</td>
  },
}

export default function Markdown({ content, className = "" }: MarkdownProps) {
  return (
    <div className={`max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0 ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  )
}
