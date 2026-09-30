/** Typed client for the FastAPI service. Pass the JWT explicitly for protected routes. */
const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim()
const isLocalApiUrl = configuredApiUrl
  ? /^https?:\/\/(localhost|127(?:\.\d{1,3}){3}|\[::1\])(?::|\/|$)/i.test(configuredApiUrl)
  : false
const productionApiConfigurationError = process.env.NODE_ENV === 'production'
  && (!configuredApiUrl || isLocalApiUrl)
const API_BASE_URL = (configuredApiUrl || (process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '')).replace(/\/$/, '')

export type ApiResult<T> = { success: true; data: T } | { success: false; error: string }
export type MenuItem = {
  id: number
  name: string
  description: string
  price: string
  image: string
  rating: string
  available: boolean
  category_id: number
  category_name: string | null
}
export type Category = { id: number; name: string; description: string; image: string }
export type CartLine = { menu_item_id: number; quantity: number }
export type AuthUser = { id: number; name: string; email: string; role: 'CUSTOMER' | 'ADMIN'; created_at: string }
export type AuthSession = { access_token: string; token_type: 'bearer'; user: AuthUser }
export type Order = {
  id: number
  user_id: number
  total_amount: string
  status: 'PENDING' | 'CONFIRMED' | 'PREPARING' | 'READY' | 'COMPLETED' | 'CANCELLED'
  payment_status: 'PENDING' | 'PAID' | 'FAILED' | 'REFUNDED'
  stripe_session_id: string | null
  created_at: string
  updated_at: string
  items: { id: number; menu_item_id: number; quantity: number; price: string }[]
}

type RequestOptions = Omit<RequestInit, 'body'> & { token?: string; body?: unknown }

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<ApiResult<T>> {
  if (productionApiConfigurationError) {
    return { success: false, error: 'The cafe API is not configured for this deployment.' }
  }

  const headers = new Headers(options.headers)
  if (options.body !== undefined) headers.set('Content-Type', 'application/json')
  if (options.token) headers.set('Authorization', `Bearer ${options.token}`)

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    })
  } catch {
    return { success: false, error: 'Could not connect to the cafe API.' }
  }

  const result = (await response.json().catch(() => null)) as ApiResult<T> | null
  if (!response.ok || !result?.success) {
    return { success: false, error: result && !result.success ? result.error : 'The request could not be completed.' }
  }
  return result
}

export const cafeApi = {
  menu: (categoryId?: number) => apiRequest<MenuItem[]>(`/api/menu${categoryId ? `?category_id=${categoryId}` : ''}`),
  categories: () => apiRequest<Category[]>('/api/categories'),
  register: (input: { name: string; email: string; password: string }) =>
    apiRequest<AuthUser>('/api/auth/register', { method: 'POST', body: input }),
  login: (input: { email: string; password: string }) =>
    apiRequest<AuthSession>('/api/auth/login', { method: 'POST', body: input }),
  orders: (token: string) => apiRequest<Order[]>('/api/orders', { token }),
  createOrder: (token: string, items: CartLine[]) =>
    apiRequest<Order>('/api/orders', { method: 'POST', token, body: { items } }),
  checkout: (token: string, items: CartLine[]) =>
    apiRequest<{ order_id: number; checkout_url: string }>('/api/checkout', { method: 'POST', token, body: { items } }),
}
