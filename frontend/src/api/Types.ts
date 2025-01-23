
export type NewsFields = {
    abstract: string,
    category: string,
    clicks: number,
    date: number,
    documentid: string,
    impressions: number,
    news_id: string,
    sddocname: string,
    subcategory: string,
    title: string,
    url: string,
}

export type NewsArticle = {
    id: string,
    relevance: number,
    fields: NewsFields,
}

export type VespaResult<InnerType> = {
    root: {
        children?: InnerType[],
        fields: {
            totalCount: number,
        },
        id: string,
    }
}
