'use client'

import { useEffect, useState } from 'react'
import type { CMSPost } from '@/lib/supabase-cms'

/**
 * Example component showing how to use Supabase CMS
 * Usage: <CMSExample category="news" />
 */
export function CMSExample({ category }: { category?: string }) {
  const [posts, setPosts] = useState<CMSPost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPosts() {
      try {
        const params = new URLSearchParams()
        if (category) params.set('category', category)

        const response = await fetch(`/api/cms?${params.toString()}`)
        const data = await response.json()

        if (data.error) {
          setError(data.error)
        } else {
          setPosts(data.data || [])
        }
      } catch (err) {
        setError('Failed to load posts')
      } finally {
        setLoading(false)
      }
    }

    fetchPosts()
  }, [category])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-600 p-4 rounded-lg bg-red-50">
        Error: {error}
      </div>
    )
  }

  if (!posts.length) {
    return (
      <div className="text-gray-500 p-4">
        No posts found{category ? ` in category "${category}"` : ''}
      </div>
    )
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {posts.map((post) => (
        <article
          key={post.id}
          className="border rounded-lg p-6 hover:shadow-lg transition-shadow"
        >
          {post.featuredImage && (
            <img
              src={post.featuredImage}
              alt={post.title}
              className="w-full h-48 object-cover rounded-md mb-4"
            />
          )}
          <h2 className="text-xl font-bold mb-2">{post.title}</h2>
          {post.excerpt && (
            <p className="text-gray-600 mb-4">{post.excerpt}</p>
          )}
          <div className="flex items-center justify-between text-sm text-gray-500">
            {post.author && <span>By {post.author}</span>}
            {post.publishedAt && (
              <time>{new Date(post.publishedAt).toLocaleDateString()}</time>
            )}
          </div>
          {post.tags && post.tags.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {post.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-gray-100 rounded-full text-xs"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </article>
      ))}
    </div>
  )
}
