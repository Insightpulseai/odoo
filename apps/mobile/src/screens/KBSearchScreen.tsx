/**
 * KB Search Screen
 * Semantic search across knowledge base artifacts
 */

import React, { useState, useCallback } from 'react'
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  useColorScheme,
  Keyboard,
} from 'react-native'
import { Ionicons } from '@expo/vector-icons'
import * as Haptics from 'expo-haptics'
import { supabase } from '../lib/supabase'
import { KBArtifact } from '../types/database'

export function KBSearchScreen() {
  const colorScheme = useColorScheme()
  const isDark = colorScheme === 'dark'
  const theme = isDark ? darkTheme : lightTheme

  const [query, setQuery] = useState('')
  const [results, setResults] = useState<KBArtifact[]>([])
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = useCallback(async () => {
    if (!query.trim()) return

    Keyboard.dismiss()
    setLoading(true)
    setHasSearched(true)
    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)

    // Semantic search using Supabase text search
    // In production, this would use pgvector for embedding-based search
    const { data, error } = await supabase
      .from('kb_artifacts')
      .select('*')
      .textSearch('content', query, {
        type: 'websearch',
        config: 'english',
      })
      .order('created_at', { ascending: false })
      .limit(20)

    if (!error && data) {
      setResults(data as KBArtifact[])
    } else {
      // Fallback to simple ILIKE search
      const { data: fallbackData } = await supabase
        .from('kb_artifacts')
        .select('*')
        .or(`title.ilike.%${query}%,content.ilike.%${query}%`)
        .order('created_at', { ascending: false })
        .limit(20)

      setResults((fallbackData as KBArtifact[]) || [])
    }

    setLoading(false)
  }, [query])

  const renderArtifactItem = ({ item }: { item: KBArtifact }) => {
    const kindIcon = getKindIcon(item.kind)
    const kindColor = getKindColor(item.kind)
    const preview = getContentPreview(item.content, query)

    return (
      <TouchableOpacity
        style={[styles.artifactCard, { backgroundColor: theme.cardBg }]}
        onPress={() => {
          Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)
          // Navigate to artifact detail
        }}
        activeOpacity={0.7}
      >
        <View style={styles.artifactHeader}>
          <View style={[styles.kindBadge, { backgroundColor: kindColor + '20' }]}>
            <Ionicons name={kindIcon as any} size={14} color={kindColor} />
            <Text style={[styles.kindText, { color: kindColor }]}>
              {formatKind(item.kind)}
            </Text>
          </View>
        </View>

        <Text style={[styles.artifactTitle, { color: theme.text }]} numberOfLines={2}>
          {item.title}
        </Text>

        <Text style={[styles.artifactPreview, { color: theme.subtext }]} numberOfLines={3}>
          {preview}
        </Text>

        {item.tags && item.tags.length > 0 && (
          <View style={styles.tagsContainer}>
            {item.tags.slice(0, 3).map((tag, index) => (
              <View key={index} style={[styles.tag, { backgroundColor: theme.bg }]}>
                <Text style={[styles.tagText, { color: theme.subtext }]}>#{tag}</Text>
              </View>
            ))}
            {item.tags.length > 3 && (
              <Text style={[styles.moreText, { color: theme.subtext }]}>
                +{item.tags.length - 3} more
              </Text>
            )}
          </View>
        )}
      </TouchableOpacity>
    )
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.bg }]}>
      {/* Search Bar */}
      <View style={[styles.searchContainer, { backgroundColor: theme.cardBg }]}>
        <Ionicons name="search" size={20} color={theme.subtext} />
        <TextInput
          style={[styles.searchInput, { color: theme.text }]}
          placeholder="Search knowledge base..."
          placeholderTextColor={theme.subtext}
          value={query}
          onChangeText={setQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
          autoCorrect={false}
          autoCapitalize="none"
        />
        {query.length > 0 && (
          <TouchableOpacity onPress={() => setQuery('')}>
            <Ionicons name="close-circle" size={20} color={theme.subtext} />
          </TouchableOpacity>
        )}
      </View>

      {/* Search Button */}
      <TouchableOpacity
        style={[styles.searchButton, { backgroundColor: '#3b82f6' }]}
        onPress={handleSearch}
        disabled={!query.trim() || loading}
      >
        {loading ? (
          <ActivityIndicator color="#ffffff" />
        ) : (
          <>
            <Ionicons name="search" size={18} color="#ffffff" />
            <Text style={styles.searchButtonText}>Search</Text>
          </>
        )}
      </TouchableOpacity>

      {/* Results */}
      {hasSearched && !loading && (
        <Text style={[styles.resultsCount, { color: theme.subtext }]}>
          {results.length} result{results.length !== 1 ? 's' : ''} found
        </Text>
      )}

      <FlatList
        data={results}
        renderItem={renderArtifactItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.resultsList}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        ListEmptyComponent={
          hasSearched && !loading ? (
            <View style={styles.emptyState}>
              <Ionicons name="document-text-outline" size={48} color={theme.subtext} />
              <Text style={[styles.emptyTitle, { color: theme.text }]}>
                No results found
              </Text>
              <Text style={[styles.emptyText, { color: theme.subtext }]}>
                Try different keywords or browse categories
              </Text>
            </View>
          ) : !hasSearched ? (
            <View style={styles.emptyState}>
              <Ionicons name="library-outline" size={48} color={theme.subtext} />
              <Text style={[styles.emptyTitle, { color: theme.text }]}>
                Search Knowledge Base
              </Text>
              <Text style={[styles.emptyText, { color: theme.subtext }]}>
                Find PRDs, runbooks, architecture docs, and more
              </Text>
            </View>
          ) : null
        }
      />
    </View>
  )
}

// Helper functions
function getKindIcon(kind: string) {
  const icons: Record<string, string> = {
    prd: 'document-text-outline',
    architecture: 'git-network-outline',
    runbook: 'book-outline',
    api_reference: 'code-slash-outline',
    data_dictionary: 'server-outline',
    documentation: 'newspaper-outline',
  }
  return icons[kind] || 'document-outline'
}

function getKindColor(kind: string) {
  const colors: Record<string, string> = {
    prd: '#8b5cf6',
    architecture: '#3b82f6',
    runbook: '#22c55e',
    api_reference: '#f59e0b',
    data_dictionary: '#ec4899',
    documentation: '#6b7280',
  }
  return colors[kind] || '#6b7280'
}

function formatKind(kind: string) {
  const names: Record<string, string> = {
    prd: 'PRD',
    architecture: 'Architecture',
    runbook: 'Runbook',
    api_reference: 'API Reference',
    data_dictionary: 'Data Dictionary',
    documentation: 'Documentation',
  }
  return names[kind] || kind
}

function getContentPreview(content: string, query: string) {
  // Find the query in content and return surrounding context
  const lowerContent = content.toLowerCase()
  const lowerQuery = query.toLowerCase()
  const index = lowerContent.indexOf(lowerQuery)

  if (index === -1) {
    return content.slice(0, 200).replace(/[#*_`]/g, '') + '...'
  }

  const start = Math.max(0, index - 50)
  const end = Math.min(content.length, index + query.length + 100)
  let preview = content.slice(start, end).replace(/[#*_`]/g, '')

  if (start > 0) preview = '...' + preview
  if (end < content.length) preview = preview + '...'

  return preview
}

// Themes
const darkTheme = {
  bg: '#0f172a',
  cardBg: '#1e293b',
  text: '#f8fafc',
  subtext: '#94a3b8',
}

const lightTheme = {
  bg: '#f8fafc',
  cardBg: '#ffffff',
  text: '#0f172a',
  subtext: '#64748b',
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 12,
    gap: 12,
  },
  searchInput: {
    flex: 1,
    fontSize: 16,
  },
  searchButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 12,
    gap: 8,
  },
  searchButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  resultsCount: {
    fontSize: 14,
    marginTop: 16,
    marginBottom: 8,
  },
  resultsList: {
    paddingTop: 8,
    paddingBottom: 100,
  },
  artifactCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  artifactHeader: {
    marginBottom: 8,
  },
  kindBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: 'flex-start',
    gap: 4,
  },
  kindText: {
    fontSize: 11,
    fontWeight: '600',
  },
  artifactTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
  },
  artifactPreview: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
    alignItems: 'center',
  },
  tag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  tagText: {
    fontSize: 12,
  },
  moreText: {
    fontSize: 12,
    fontStyle: 'italic',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64,
    gap: 8,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 12,
  },
  emptyText: {
    fontSize: 14,
    textAlign: 'center',
    paddingHorizontal: 32,
  },
})
