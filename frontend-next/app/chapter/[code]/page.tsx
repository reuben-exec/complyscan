import ChapterClient from "./ChapterClient";

export function generateStaticParams() {
  return [{ code: "HIC" }, { code: "PRE" }];
}

export default function ChapterPage({
  params,
}: {
  params: Promise<{ code: string }>;
}) {
  // Server component that wraps client component
  // generateStaticParams handled here for static export
  return <ChapterCodePage params={params} />;
}

async function ChapterCodePage({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  return <ChapterClient code={code} />;
}
