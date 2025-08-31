## Common Interfaces for Business Planning Frontend

This document defines shared TypeScript interfaces and value objects intended to be reused across the frontend.

### Conventions
- All date/time strings are ISO-8601 in UTC unless noted.
- Money amounts are represented in minor units (cents) to avoid floating point issues.
- IDs are strings; consider using branded types in code if desired for additional safety.

### Identifiers & Core Utilities
```ts
// Simple aliases; consider branded types in implementation for extra safety
export type UUID = string;
export type EntityId = string;
export type Slug = string;
export type Email = string;
export type Url = string;

export type ISODate = string; // e.g. "2025-01-31"
export type ISODateTime = string; // e.g. "2025-01-31T12:34:56Z"

export interface DateRange {
  start: ISODate | ISODateTime;
  end?: ISODate | ISODateTime;
}

export type CurrencyCode =
  | 'USD' | 'EUR' | 'GBP' | 'JPY' | 'AUD' | 'CAD' | 'CHF' | 'CNY' | 'SEK' | 'NZD'
  | string; // fallback for other ISO-4217 codes

export interface Money {
  amountCents: number;
  currency: CurrencyCode;
}

export interface WithTimestamps {
  createdAt: ISODateTime;
  updatedAt: ISODateTime;
}

export interface WithSoftDelete {
  deletedAt?: ISODateTime;
}
```

### Auditing
```ts
export interface UserRef {
  id: EntityId;
  displayName: string;
  avatarUrl?: Url;
  email?: Email;
}

export interface WithAudit {
  createdBy: UserRef;
  updatedBy?: UserRef;
}
```

### People & Organizations
```ts
export interface Address {
  line1: string;
  line2?: string;
  city: string;
  region?: string; // state/province
  postalCode?: string;
  country: string; // ISO-3166 alpha-2 preferred
}

export interface ContactInfo {
  email?: Email;
  phone?: string;
  website?: Url;
  address?: Address;
}

export interface User extends WithTimestamps {
  id: EntityId;
  email: Email;
  displayName: string;
  firstName?: string;
  lastName?: string;
  avatarUrl?: Url;
  timeZone?: string; // IANA tz
  locale?: string; // BCP 47
}

export interface OrganizationRef {
  id: EntityId;
  name: string;
  slug: Slug;
}

export interface Organization extends WithTimestamps {
  id: EntityId;
  name: string;
  slug: Slug;
  logoUrl?: Url;
  industry?: string;
  size?: number; // headcount
  contact?: ContactInfo;
}

export type Permission =
  | 'plan:read' | 'plan:write'
  | 'project:read' | 'project:write'
  | 'org:admin'
  | string; // feature-specific permissions

export type RoleKey = 'owner' | 'admin' | 'editor' | 'viewer' | string;

export interface Role {
  key: RoleKey;
  permissions: Permission[];
}

export interface Session {
  user: User;
  org: OrganizationRef;
  roles: RoleKey[];
  permissions?: Permission[];
  token?: string; // access/jwt token if used
  expiresAt: ISODateTime;
}
```

### Tags, Attachments, Comments
```ts
export interface Tag {
  id: EntityId;
  label: string;
  color?: string; // hex or css var
}

export interface Attachment {
  id: EntityId;
  fileName: string;
  mimeType: string;
  sizeBytes: number;
  url: Url; // download/view URL
  uploadedAt: ISODateTime;
  uploadedBy: UserRef;
}

export interface Comment extends WithTimestamps {
  id: EntityId;
  author: UserRef;
  body: string; // markdown or rich text serialized
  parentId?: EntityId; // for threads
}
```

### Projects & Planning Domain
```ts
export type ProjectStatus = 'draft' | 'active' | 'on_hold' | 'completed' | 'archived';

export interface Project extends WithTimestamps {
  id: EntityId;
  orgId: EntityId;
  name: string;
  slug: Slug;
  description?: string;
  status: ProjectStatus;
  owner: UserRef;
  team: UserRef[];
  startDate?: ISODate;
  endDate?: ISODate;
  tags?: Tag[];
}

export type PlanStatus = 'draft' | 'in_review' | 'approved' | 'archived';
export type PlanSectionKey =
  | 'executive_summary'
  | 'company_description'
  | 'market_analysis'
  | 'organization_management'
  | 'product_service_line'
  | 'marketing_sales'
  | 'operations_plan'
  | 'risk_analysis'
  | 'roadmap'
  | 'funding_request'
  | 'financial_projections'
  | 'appendix';

export type RichText = string; // serialized markdown/JSON; refine later if needed

export interface PlanSection {
  id: EntityId;
  key: PlanSectionKey;
  title: string;
  body: RichText;
  children?: PlanSection[];
  attachments?: Attachment[];
}

export interface KPI {
  id: EntityId;
  name: string;
  description?: string;
  target: number;
  unit: 'usd' | 'percent' | 'number' | 'days' | 'hours' | string;
  current?: number;
  dueDate?: ISODate;
}

export interface RevenueStream {
  id: EntityId;
  name: string;
  description?: string;
}

export interface CostItem {
  id: EntityId;
  name: string;
  description?: string;
}

export interface ForecastPoint {
  month: string; // YYYY-MM
  revenueCents: number;
  costCents: number;
  profitCents: number;
}

export interface FinancialProjection {
  currency: CurrencyCode;
  assumptions?: string;
  revenueStreams: RevenueStream[];
  costItems: CostItem[];
  forecast: ForecastPoint[];
}

export interface BusinessPlan extends WithTimestamps {
  id: EntityId;
  orgId: EntityId;
  projectId?: EntityId;
  title: string;
  summary?: string;
  status: PlanStatus;
  version: number;
  sections: PlanSection[];
  kpis?: KPI[];
  financials?: FinancialProjection;
  reviewers?: UserRef[];
}

export type MilestoneStatus = 'planned' | 'in_progress' | 'done' | 'blocked';

export interface Milestone extends WithTimestamps {
  id: EntityId;
  projectId: EntityId;
  title: string;
  dueDate?: ISODate;
  status: MilestoneStatus;
  owner: UserRef;
}

export type TaskStatus = 'todo' | 'in_progress' | 'done' | 'blocked';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task extends WithTimestamps {
  id: EntityId;
  projectId: EntityId;
  milestoneId?: EntityId;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assignees: UserRef[];
  dueDate?: ISODate;
  tags?: Tag[];
  attachments?: Attachment[];
  commentsCount?: number;
}
```

### API Contracts
```ts
export interface ApiMeta {
  requestId?: string;
  traceId?: string;
}

export interface ApiError {
  code: string; // app or http-like code
  message: string;
  details?: unknown;
  status?: number; // http status if relevant
}

export interface Paginated<T> {
  items: T[];
  page: number;
  pageSize: number;
  totalItems: number;
  totalPages: number;
}

export interface Sort {
  field: string;
  direction: 'asc' | 'desc';
}

export type FilterOp =
  | 'eq' | 'ne' | 'lt' | 'gt' | 'lte' | 'gte'
  | 'in' | 'contains' | 'startsWith' | 'endsWith';

export interface Filter {
  field: string;
  op: FilterOp;
  value: unknown;
}

export interface ListQuery {
  page?: number;
  pageSize?: number;
  search?: string;
  sort?: Sort[];
  filters?: Filter[];
}

export interface ApiSuccess<T> {
  ok: true;
  data: T;
  meta?: ApiMeta;
}

export interface ApiFailure {
  ok: false;
  error: ApiError;
  meta?: ApiMeta;
}

export type ApiResult<T> = ApiSuccess<T> | ApiFailure;
```

### UI Helpers
```ts
export type AsyncStatus = 'idle' | 'loading' | 'success' | 'error';

export interface AsyncState<T> {
  status: AsyncStatus;
  data?: T;
  error?: ApiError;
}

export interface SelectOption<V = string> {
  value: V;
  label: string;
  icon?: string; // icon name or url
  disabled?: boolean;
}

export interface TableColumn<T> {
  id: string;
  header: string;
  accessor: (row: T) => unknown;
  width?: number;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
}

export interface ModalState<P = unknown> {
  isOpen: boolean;
  payload?: P;
}

export interface AppRoute {
  path: string;
  name: string;
  params?: Record<string, string>;
}
```

### Feature Flags & Preferences
```ts
export type FeatureFlagKey = 'advanced-financials' | 'ai-assist' | 'custom-templates' | string;
export type FeatureFlags = Record<FeatureFlagKey, boolean>;

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  dateFormat?: 'MDY' | 'DMY' | 'YMD';
  currency?: CurrencyCode;
}
```

### File Uploads
```ts
export interface UploadRequest {
  fileName: string;
  mimeType: string;
  sizeBytes: number;
}

export interface UploadResponse {
  uploadUrl: Url;
  fileId: EntityId;
  headers?: Record<string, string>;
}
```

### Forms
```ts
export interface FormErrors<TFields extends Record<string, unknown> = Record<string, unknown>> {
  fieldErrors?: Partial<Record<keyof TFields, string[]>>;
  global?: string[];
}
```

### Notes
- These are frontend-facing shapes. Server payloads may differ slightly; keep transform/adapters near API clients.
- Prefer immutability and explicit optionality; avoid undefined vs null ambiguity where possible.
- Extend as needed for specialized modules (e.g., templates, AI suggestions, collaboration cursors).
