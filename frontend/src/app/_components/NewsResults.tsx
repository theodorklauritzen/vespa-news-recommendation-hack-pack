import { NewsFields, VespaChild } from "@/api/Types";
import NewsArticleCmp from "./NewsArticleCmp";
import { v4 } from "uuid";
import styles from "./NewsResults.module.css"

export default function NewsResults({
  articles
}: {
  articles: VespaChild<NewsFields>[],
}) {

  return <div className={styles.newsWrapper}>
    {articles.map(child => <NewsArticleCmp article={child} key={v4()} />)}
  </div>
}
