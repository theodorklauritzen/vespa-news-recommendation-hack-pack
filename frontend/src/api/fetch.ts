"use server"

import { Embedding, NewsFields, VespaResult } from "./Types"

const VESPA_HOSTNAME = `http://${process.env.VESPA_HOST}:${process.env.VESPA_PORT}/`

async function queryVespa<InnerType>(yql: string, options?: {
    query?: string,
    ranking?: string,
} & Record<string, string>): Promise<VespaResult<InnerType>> {
    console.log(yql)
    let url = `${VESPA_HOSTNAME}/search/?yql=${encodeURIComponent(yql)}`
    if (options) {
        Object.keys(options).forEach(key => {
            url += `&${key}=${encodeURIComponent(options[key])}`
        })
    }
    console.log(url)
    try {
        const response = await fetch(url)
        const jsonResponse = await response.json()
        console.log(jsonResponse)
        return jsonResponse as VespaResult<InnerType>
    } catch (e) {
        console.error(e)
        return {
            root: {
                id: '',
                fields: {
                    totalCount: 0
                }
            }
        }
    }
}

export async function simpleSearch(query: string) {
    return await queryVespa("select * from news where userQuery()", {
        query,
    }) as VespaResult<NewsFields>
}

export async function getUsersIds() {
    return await queryVespa("select user_id, embedding from user where true limit 30") as VespaResult<{
        user_id: string,
        embedding: Embedding,
    }>
}

export async function recommendArticles(userEmbedding: Embedding, targetHits: number) {
    return await queryVespa(`select * from news where ({targetHits:${targetHits}}nearestNeighbor(embedding, user_embedding))`, {
        "ranking.features.query(user_embedding)": `[${userEmbedding.values.join(",")}]`,
        ranking: "recommendation"
    }) as VespaResult<NewsFields>
}

export async function popularNews(query: string) {
    return await queryVespa("select * from news where userQuery() limit 20", {
        query,
        ranking: 'popularity'
    }) as VespaResult<NewsFields>
}
