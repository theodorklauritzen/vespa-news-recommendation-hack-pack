"use client"
import { NewsArticle } from "@/api/Types";
import { useState } from "react";
import NewsResults from "./_components/NewsResults";
import { simpleSearch } from "@/api/fetch";


export default function SearchWrapper() {

  const [ searchWord, setSearchWord ] = useState("music")
  const [news, setNews] = useState<NewsArticle[]>([])

  const search = async (e: React.FormEvent) => {
    e.preventDefault();
    const results = await simpleSearch(searchWord)
    console.log(results)
    setNews(results.root.children)
  }

  return <div>
    <div>
      <form onSubmit={search}>
        <input type="text" value={searchWord} onChange={(e) => setSearchWord(e.target.value)} />
        <input type="submit" />
      </form>
    </div>

    <NewsResults articles={news} />
  </div>
}
