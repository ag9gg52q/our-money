export type ApiErrorData = Record<string, string[] | string>

export class ApiError extends Error {
  status: number
  data: ApiErrorData

  constructor(status: number, data: ApiErrorData) {
    super(`API error ${status}`)
    this.status = status
    this.data = data
  }
}

function getCookie(name: string): string | undefined {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1]
}

const SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase()
  const headers = new Headers(options.headers)

  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  if (!SAFE_METHODS.includes(method)) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) headers.set('X-CSRFToken', csrfToken)
  }

  const response = await fetch(path, {
    ...options,
    method,
    headers,
    credentials: 'same-origin',
  })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    throw new ApiError(response.status, data)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json()
}
