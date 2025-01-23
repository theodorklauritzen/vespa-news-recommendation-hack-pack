"use server"

import { NewsArticle, VespaResult } from "./Types"

const VESPA_HOSTNAME = 'http://localhost:8080'

async function queryVespa<InnerType>(yql: string, options?: {
    query?: string,
    ranking?: string,
}): Promise<VespaResult<InnerType>> {
    let url = `${VESPA_HOSTNAME}/search/?yql=${encodeURIComponent(yql)}`
    if (options) {
        if (options.query) {
            url += `&query=${options.query}`
        }
        if (options.ranking) {
            url += `&ranking=${options.ranking}`
        }
    }
    const response = await fetch(url)
    const jsonResponse = await response.json()
    return jsonResponse as VespaResult<InnerType>
}

export async function simpleSearch(query: string) {
    return await queryVespa("select * from news where userQuery()", {
        query,
        ranking: "popularity"
    }) as VespaResult<NewsArticle>

}
