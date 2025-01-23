"use client"

import type { NewsArticle } from "@/api/Types"
import styles from "./NewsArticleCmp.module.css"

export default function NewsArticleCmp({
  article
}: {
  article: NewsArticle
}) {

  return <div className={styles.article}>
    <h2>{article.fields.title}</h2>
    <p>{article.fields.abstract}</p>
  </div>
}
