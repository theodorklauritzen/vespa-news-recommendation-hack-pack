"use client"
import { Embedding, NewsFields, VespaChild, VespaResult } from "@/api/Types";
import { useState } from "react";
import NewsResults from "./_components/NewsResults";
import { recommendArticles, simpleSearch } from "@/api/fetch";
import styles from "./SearchWrapper.module.css";
import { v4 } from "uuid";

export default function SearchWrapper({
  users
}: {
  users: {
    user_id: string,
    embedding: Embedding
  }[]
}) {

  const [searchWord, setSearchWord] = useState("music")
  const [selectedUser, setSelectedUser] = useState(0)

  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null)
  const [news, setNews] = useState<VespaChild<NewsFields>[]>([])

  function setResults(results: VespaResult<NewsFields>) {
    if (results.root.children) {
      setNews(results.root.children)
      setFeedbackMessage(null)
    } else {
      setNews([])
      setFeedbackMessage("No results")
    }
  }

  const textMatchSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    const results = await simpleSearch(searchWord)
    setResults(results)
  }

  const recommendationSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    const user = users[selectedUser]
    const results = await recommendArticles(user.embedding, 10)
    setResults(results)
  }

  return <div>
    <div className={styles.searchbar}>
      <form onSubmit={textMatchSearch}>
        <input type="text" value={searchWord} onChange={(e) => setSearchWord(e.target.value)} />
        <input type="submit" value="Text Match Search" />
      </form>

      <form onSubmit={recommendationSearch}>
        <select value={selectedUser} onChange={(e) => setSelectedUser(parseInt(e.target.value))}>
          {users.map((user, index) => <option key={v4()} value={index}>{user.user_id}</option>)}
        </select>
        <input type="submit" value="Find recommended articles" />
      </form>

      {feedbackMessage !== null &&
        <p>{feedbackMessage}</p>
      }
    </div>

    <NewsResults articles={news} />
  </div>
}
