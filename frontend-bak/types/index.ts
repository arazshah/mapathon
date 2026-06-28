export interface MapData {
  geojson: GeoJSON.FeatureCollection
  center: [number, number]
  zoom: number
  count: number
}

export interface ReportItem {
  name: string
  type: string | null
  lat: number | null
  lng: number | null
}

export interface Report {
  type: "list" | "distance" | "area"
  // list
  count?: number
  items?: ReportItem[]
  // distance
  distance_km?: number
  distance_meters?: number
  point1?: { lat: number; lng: number }
  point2?: { lat: number; lng: number }
  // area
  area_m2?: number
  area_hectares?: number
  area_km2?: number
}

export interface QueryResponse {
  success: boolean
  question: string
  answer: string | null
  map: MapData | null
  report: Report | null
  error: string | null
}
