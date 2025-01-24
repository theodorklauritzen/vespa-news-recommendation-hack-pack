"use client"

import type { NewsFields, VespaChild } from "@/api/Types"
import styles from "./NewsArticleCmp.module.css"

export default function NewsArticleCmp({
  article
}: {
  article: VespaChild<NewsFields>
}) {

  return <div className={styles.article}>
    <h2>{article.fields.title}</h2>
    <p>{article.fields.abstract}</p>
  </div>
}
