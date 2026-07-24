import ReactMarkdown from "react-markdown";

interface MarkdownBodyProps {
  content: string;
  emptyLabel?: string;
}

export default function MarkdownBody({
  content,
  emptyLabel = "Content will appear here.",
}: MarkdownBodyProps) {
  const text = content.trim();
  if (!text) {
    return (
      <div className="markdown-body is-empty" aria-label={emptyLabel}>
        <p>{emptyLabel}</p>
      </div>
    );
  }

  return (
    <div className="markdown-body">
      <ReactMarkdown>{content}</ReactMarkdown>
    </div>
  );
}
