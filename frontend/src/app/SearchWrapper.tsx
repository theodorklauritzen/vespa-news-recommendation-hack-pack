"use client"
import { NewsArticle } from "@/api/Types";
import { useState } from "react";
import NewsResults from "./_components/NewsResults";
import { simpleSearch } from "@/api/fetch";
import styles from "./SearchWrapper.module.css";

export default function SearchWrapper() {

  const [searchWord, setSearchWord] = useState("music")
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null)
  const [news, setNews] = useState<NewsArticle[]>([])

  const search = async (e: React.FormEvent) => {
    e.preventDefault();
    const results = await simpleSearch(searchWord)
    console.log(results)
    if (results.root.children) {
      setNews(results.root.children)
      setFeedbackMessage(null)
    } else {
      setNews([])
      setFeedbackMessage("No results")
    }
  }

  return <div>
    <div className={styles.searchbar}>
      <form onSubmit={search}>
        <input type="text" value={searchWord} onChange={(e) => setSearchWord(e.target.value)} />
        <input type="submit" value="Text Match Search" />
      </form>

      {feedbackMessage !== null &&
        <p>{feedbackMessage}</p>
      }
    </div>

    <NewsResults articles={news} />
  </div>
}
