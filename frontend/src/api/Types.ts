
export type Embedding = {
    type: string,
    values: number[],
}

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

export type VespaChild<InnerType> = {
    id: string,
    relevance: number,
    fields: InnerType,
}

export type VespaResult<InnerType> = {
    root: {
        children?: VespaChild<InnerType>[],
        fields: {
            totalCount: number,
        },
        id: string,
        errors?: any[]
    }
}
