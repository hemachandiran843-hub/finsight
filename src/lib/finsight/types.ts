// FinSight X — shared domain types (mirror of the FastAPI response shapes)

export type Role = "ceo" | "credit_analyst" | "risk_manager";

export interface User {
  email: string;
  name: string;
  role: Role;
  role_label: string;
}

export interface LoginResponse {
  token: string;
  user: User;
  demo_mode: boolean;
}

export interface CompanyInfo {
  name: string;
  sector: string;
  listings: string;
  profile: string;
  currency: string;
}

export type Metrics = Record<string, Record<string, number>>;

export interface SignalInput {
  label: string;
  direction: "up" | "down" | "flat";
  value: string;
}

export interface Signal {
  id: string;
  title: string;
  category: string;
  severity: "high" | "medium" | "low";
  status: string;
  logic: string;
  explanation: string;
  inputs: SignalInput[];
  evidence_ids: string[];
}

export interface Mismatch {
  id: string;
  statement: string;
  statement_source: string | null;
  page: number | null;
  section: string | null;
  period: string | null;
  data_points: { label: string; detail: string }[];
  verdict: string;
  disclaimer: string;
  verification_steps: string[];
}

export interface RiskNode {
  id: string;
  label: string;
  metric: string | null;
  severity: "high" | "medium" | "low";
  detail: string;
}

export interface Evidence {
  id: string;
  document: string;
  page: number | null;
  section: string;
  kind: "reported_fact" | "management_statement" | string;
  quote: string;
  tags?: string[];
  current?: boolean;
}

export interface MemoryItem {
  key: string;
  label: string;
  series: number[];
  unit: string;
  cum_pct: number | null;
  direction: "up" | "down" | "flat";
  streak: number;
  adverse: boolean;
  message: string;
}

export interface ExecSummary {
  headline: string;
  paragraphs: string[];
  key_changes: string[];
  guidance: string[];
  risks_events: string[];
}

export interface TrendRow {
  period: string;
  revenue: number | null;
  net_profit: number | null;
  ebitda: number | null;
  ebitda_margin: number | null;
  total_debt: number | null;
  op_cashflow: number | null;
  finance_cost: number | null;
  cash: number | null;
  current_ratio: number | null;
  interest_coverage: number | null;
  net_margin: number | null;
  capex: number | null;
}

export interface AnalysisPackage {
  kind: string;
  company: CompanyInfo;
  period_label: string;
  periods: string[];
  metrics: Metrics;
  metric_labels: Record<string, string>;
  trend_series: TrendRow[];
  exec_summary: ExecSummary;
  signals: Signal[];
  mismatches: Mismatch[];
  risk_chain: RiskNode[];
  memory: MemoryItem[];
  evidence: Evidence[];
  management_statements: Record<string, { quote: string; section: string; page: number }[]>;
  safety_note: string;
  ai_enabled: boolean;
  partial?: boolean;
  notice?: string;
}

export interface AskEvidence {
  id: string;
  document: string;
  page: number | null;
  section: string;
  kind: string;
  quote: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  evidence: AskEvidence[];
  mode: string;
  demo_mode: boolean;
  safety_note: string;
}

export interface AuditEntry {
  ts: string;
  actor: string;
  role: string;
  action: string;
  detail: string;
}

export interface ReportMeta {
  id: number;
  filename: string;
  company: string;
  period: string | null;
  uploaded_by: string;
  uploaded_at: string;
  pages: number;
  is_demo: number;
}

export const ROLE_DEMO_ACCOUNTS: {
  role: Role;
  email: string;
  password: string;
  label: string;
  blurb: string;
}[] = [
  {
    role: "ceo",
    email: "ceo@finsightx.demo",
    password: "demo1234",
    label: "CEO",
    blurb: "Strategic overview: executive summary, KPIs, top signals and trends.",
  },
  {
    role: "credit_analyst",
    email: "analyst@finsightx.demo",
    password: "demo1234",
    label: "Credit Analyst",
    blurb: "Full analytical workbench: upload reports, signals, evidence, Ask the Report.",
  },
  {
    role: "risk_manager",
    email: "risk@finsightx.demo",
    password: "demo1234",
    label: "Risk Manager",
    blurb: "Risk chain, statement–data mismatches and the platform audit log.",
  },
];
