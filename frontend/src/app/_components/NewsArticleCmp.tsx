"use client"

import type { NewsArticle } from "@/api/Types"


export default function NewsArticleCmp({
  article
}: {
  article: NewsArticle
}) {

  return <div>
    <h2>{article.fields.title}</h2>
    <p>{article.fields.abstract}</p>
  </div>
}
