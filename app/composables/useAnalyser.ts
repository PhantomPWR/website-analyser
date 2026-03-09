export interface SeoResult {
  title: string | null
  description: string | null
  og_tags: Record<string, string>
  canonical: string | null
  robots_meta: string | null
  headings: Record<string, string[]>
  sitemap_found: boolean
  robots_txt_found: boolean
  structured_data: unknown[]
}

export interface WebVital {
  value: number | null
  display: string | null
  score: number | null
}

export interface ResourceSummary {
  scripts: number
  stylesheets: number
  images: number
  total_resources: number
  html_size_kb: number
}

export interface PerformanceResult {
  performance_score: number | null
  fcp: WebVital
  lcp: WebVital
  cls: WebVital
  ttfb: WebVital
  inp: WebVital
  speed_index: WebVital
  resources: ResourceSummary
  pagespeed_available: boolean
  pagespeed_error: string | null
}

export interface HeaderCheck {
  present: boolean
  value: string | null
  note: string | null
}

export interface CookieCheck {
  name: string
  secure: boolean
  http_only: boolean
  same_site: string | null
}

export interface SecurityResult {
  https: boolean
  hsts: HeaderCheck
  csp: HeaderCheck
  x_frame_options: HeaderCheck
  x_content_type_options: HeaderCheck
  referrer_policy: HeaderCheck
  permissions_policy: HeaderCheck
  coop: HeaderCheck
  all_security_headers: Record<string, string | null>
  mixed_content_count: number
  mixed_content_urls: string[]
  cookies: CookieCheck[]
  server_header: string | null
  x_powered_by: string | null
}

export interface TechItem {
  name: string
  category: string
  confidence: string
  version: string | null
  icon: string | null
}

export interface TechResult {
  technologies: TechItem[]
  categories: Record<string, string[]>
}

export interface ImageAltIssue {
  src: string
  issue: string
}

export interface FormLabelIssue {
  element: string
  input_type: string | null
  issue: string
}

export interface HeadingIssue {
  tag: string
  text: string
  issue: string
}

export interface AccessibilityResult {
  lang_attribute: string | null
  lang_present: boolean
  total_images: number
  images_missing_alt: number
  images_empty_alt: number
  image_issues: ImageAltIssue[]
  total_inputs: number
  inputs_missing_label: number
  form_issues: FormLabelIssue[]
  heading_order_valid: boolean
  heading_issues: HeadingIssue[]
  aria_roles_count: number
  aria_labels_count: number
  aria_landmarks: string[]
  skip_link_present: boolean
  positive_tabindex_count: number
  score: number
  issues_total: number
}

export interface BrokenLink {
  url: string
  status_code: number | null
  error: string | null
}

export interface ContentResult {
  word_count: number
  sentence_count: number
  paragraph_count: number
  avg_words_per_sentence: number
  flesch_reading_ease: number
  readability_label: string
  content_to_html_ratio: number
  internal_links_total: number
  internal_links_checked: number
  broken_links: BrokenLink[]
  external_links_total: number
  has_favicon: boolean
  has_meta_viewport: boolean
  text_preview: string
}

export interface AnalysisState {
  seo: SeoResult | null
  performance: PerformanceResult | null
  security: SecurityResult | null
  tech: TechResult | null
  accessibility: AccessibilityResult | null
  content: ContentResult | null
}

export function useAnalyser() {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const loading = ref(false)
  const error = ref<string | null>(null)
  const saving = ref(false)
  const savedReportId = ref<string | null>(null)
  const results = ref<AnalysisState>({ seo: null, performance: null, security: null, tech: null, accessibility: null, content: null })
  const analysedUrl = ref<string | null>(null)

  async function analyseUrl(url: string) {
    loading.value = true
    error.value = null
    results.value = { seo: null, performance: null, security: null, tech: null, accessibility: null, content: null }
    analysedUrl.value = url
    savedReportId.value = null

    try {
      const [seo, performance, security, tech, accessibility, content] = await Promise.all([
        $fetch<SeoResult>(`${apiBase}/analyse/seo`, { query: { url } }),
        $fetch<PerformanceResult>(`${apiBase}/analyse/performance`, { query: { url } }),
        $fetch<SecurityResult>(`${apiBase}/analyse/security`, { query: { url } }),
        $fetch<TechResult>(`${apiBase}/analyse/tech`, { query: { url } }),
        $fetch<AccessibilityResult>(`${apiBase}/analyse/accessibility`, { query: { url } }),
        $fetch<ContentResult>(`${apiBase}/analyse/content`, { query: { url } }),
      ])
      results.value.seo = seo
      results.value.performance = performance
      results.value.security = security
      results.value.tech = tech
      results.value.accessibility = accessibility
      results.value.content = content
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to analyse URL'
      error.value = msg
    } finally {
      loading.value = false
    }
  }

  async function saveReport() {
    if (!analysedUrl.value || !results.value.seo) return
    saving.value = true
    try {
      const { id } = await $fetch<{ id: string }>(`${apiBase}/reports`, {
        method: 'POST',
        body: { url: analysedUrl.value, data: results.value },
      })
      savedReportId.value = id
    } finally {
      saving.value = false
    }
  }

  return { loading, error, saving, savedReportId, results, analysedUrl, analyseUrl, saveReport }
}
