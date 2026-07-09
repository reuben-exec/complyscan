import RequirementClient from "./RequirementClient";

export function generateStaticParams() {
  return [
    { code: "HIC", req: "HIC-R01" },
    { code: "HIC", req: "HIC-R02" },
    { code: "HIC", req: "HIC-R03" },
    { code: "HIC", req: "HIC-R04" },
    { code: "HIC", req: "HIC-R05" },
    { code: "HIC", req: "HIC-R06" },
    { code: "HIC", req: "HIC-R07" },
    { code: "HIC", req: "HIC-R08" },
    { code: "HIC", req: "HIC-R09" },
    { code: "HIC", req: "HIC-R10" },
    { code: "HIC", req: "HIC-R11" },
    { code: "HIC", req: "HIC-R12" },
    { code: "HIC", req: "HIC-R13" },
    { code: "HIC", req: "HIC-R14" },
    { code: "PRE", req: "PRE-R01" },
    { code: "PRE", req: "PRE-R02" },
    { code: "PRE", req: "PRE-R03" },
    { code: "PRE", req: "PRE-R04" },
    { code: "PRE", req: "PRE-R05" },
    { code: "PRE", req: "PRE-R06" },
    { code: "PRE", req: "PRE-R07" },
    { code: "PRE", req: "PRE-R08" },
    { code: "PRE", req: "PRE-R09" },
    { code: "PRE", req: "PRE-R10" },
    { code: "PRE", req: "PRE-R11" },
    { code: "PRE", req: "PRE-R12" },
    { code: "PRE", req: "PRE-R13" },
    { code: "PRE", req: "PRE-R14" },
    { code: "PRE", req: "PRE-R15" },
    { code: "PRE", req: "PRE-R16" },
    { code: "PRE", req: "PRE-R17" },
  ];
}

export default function RequirementPage({
  params,
}: {
  params: Promise<{ code: string; req: string }>;
}) {
  return <RequirementPageInner params={params} />;
}

async function RequirementPageInner({
  params,
}: {
  params: Promise<{ code: string; req: string }>;
}) {
  const { code, req } = await params;
  return <RequirementClient code={code} reqId={req} />;
}
