/**
 * Supabase CMS API Client
 * Documentation: https://www.supabase-cms.com/docs
 */

interface CMSPost {
  id: string
  title: string
  slug: string
  content: string
  excerpt?: string
  author?: string
  publishedAt?: string
  categories?: string[]
  tags?: string[]
  seoTitle?: string
  seoDescription?: string
  featuredImage?: string
}

interface CMSResponse<T> {
  data: T
  error?: string
  pagination?: {
    page: number
    perPage: number
    total: number
  }
}

export class SupabaseCMS {
  private baseUrl: string
  private apiKey: string

  constructor(config?: { baseUrl?: string; apiKey?: string }) {
    this.baseUrl =
      config?.baseUrl ||
      process.env.SUPABASE_CMS_URL ||
      'https://kkuljccmudnqugcotgat.supabase.co/functions/v1/posts-api'
    this.apiKey = config?.apiKey || process.env.SUPABASE_CMS_API_KEY || ''
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<CMSResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          apikey: this.apiKey,
          'Content-Type': 'application/json',
          ...options.headers,
        },
      })

      if (!response.ok) {
        throw new Error(`CMS API error: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      return {
        data: null as T,
        error: error instanceof Error ? error.message : 'Unknown error',
      }
    }
  }

  /**
   * Get all posts with optional filtering
   */
  async getPosts(params?: {
    page?: number
    perPage?: number
    category?: string
    tag?: string
    search?: string
  }): Promise<CMSResponse<CMSPost[]>> {
    const queryParams = new URLSearchParams()
    if (params?.page) queryParams.set('page', params.page.toString())
    if (params?.perPage) queryParams.set('perPage', params.perPage.toString())
    if (params?.category) queryParams.set('category', params.category)
    if (params?.tag) queryParams.set('tag', params.tag)
    if (params?.search) queryParams.set('search', params.search)

    const query = queryParams.toString()
    return this.request<CMSPost[]>(query ? `?${query}` : '')
  }

  /**
   * Get a single post by slug
   */
  async getPost(slug: string): Promise<CMSResponse<CMSPost>> {
    return this.request<CMSPost>(`/${slug}`)
  }

  /**
   * Create a new post
   */
  async createPost(post: Omit<CMSPost, 'id'>): Promise<CMSResponse<CMSPost>> {
    return this.request<CMSPost>('', {
      method: 'POST',
      body: JSON.stringify(post),
    })
  }

  /**
   * Update an existing post
   */
  async updatePost(
    id: string,
    post: Partial<CMSPost>
  ): Promise<CMSResponse<CMSPost>> {
    return this.request<CMSPost>(`/${id}`, {
      method: 'PUT',
      body: JSON.stringify(post),
    })
  }

  /**
   * Delete a post
   */
  async deletePost(id: string): Promise<CMSResponse<void>> {
    return this.request<void>(`/${id}`, {
      method: 'DELETE',
    })
  }

  /**
   * Get posts by category
   */
  async getPostsByCategory(category: string): Promise<CMSResponse<CMSPost[]>> {
    return this.getPosts({ category })
  }

  /**
   * Get posts by tag
   */
  async getPostsByTag(tag: string): Promise<CMSResponse<CMSPost[]>> {
    return this.getPosts({ tag })
  }

  /**
   * Search posts
   */
  async searchPosts(query: string): Promise<CMSResponse<CMSPost[]>> {
    return this.getPosts({ search: query })
  }
}

// Export singleton instance
export const cms = new SupabaseCMS()

// Export types
export type { CMSPost, CMSResponse }
