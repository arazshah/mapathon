"use client"

import { useEffect, useRef } from "react"
import { MapData } from "@/types"

interface Props {
  data: MapData
  mapRef?: React.MutableRefObject<any>
  selectedIndex?: number | null
}

export default function MapView({ data, mapRef: externalMapRef, selectedIndex }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const internalMapRef = useRef<any>(null)
  const mapRef = externalMapRef || internalMapRef

  useEffect(() => {
    if (!containerRef.current) return

    const init = async () => {
      const maplibregl = (await import("maplibre-gl")).default
      await import("maplibre-gl/dist/maplibre-gl.css")

      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }

      const map = new maplibregl.Map({
        container: containerRef.current!,
        style: {
          version: 8,
          sources: {
            osm: {
              type: "raster",
              tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
              tileSize: 256,
              attribution: "© OpenStreetMap contributors",
            },
          },
          layers: [{ id: "osm", type: "raster", source: "osm" }],
        },
        center: data.center,
        zoom: data.zoom,
      })

      map.on("load", () => {
        map.addSource("results", {
          type: "geojson",
          data: data.geojson,
        })

        // نقاط عادی
        map.addLayer({
          id: "results-circle",
          type: "circle",
          source: "results",
          filter: ["==", ["geometry-type"], "Point"],
          paint: {
            "circle-radius": [
              "case",
              ["boolean", ["feature-state", "selected"], false],
              10,
              6,
            ],
            "circle-color": [
              "case",
              ["boolean", ["feature-state", "selected"], false],
              "#dc2626",
              "#2563eb",
            ],
            "circle-stroke-color": "#ffffff",
            "circle-stroke-width": 2,
            "circle-opacity": 0.9,
          },
        })

        // پولیگون‌ها
        map.addLayer({
          id: "results-fill",
          type: "fill",
          source: "results",
          filter: ["==", ["geometry-type"], "Polygon"],
          paint: {
            "fill-color": "#2563eb",
            "fill-opacity": 0.15,
          },
        })

        // خطوط
        map.addLayer({
          id: "results-line",
          type: "line",
          source: "results",
          filter: ["in", ["geometry-type"], ["literal", ["LineString", "Polygon"]]],
          paint: {
            "line-color": "#2563eb",
            "line-width": 2,
          },
        })

        // Popup
        map.on("click", "results-circle", (e: any) => {
          const props = e.features[0].properties
          const name = props.name || "بدون نام"
          const type = props.type || "مکان"
          new maplibregl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(
              `<div dir="rtl" class="text-right">
                <strong class="text-gray-800">${name}</strong>
                <div class="text-xs text-gray-500 mt-1">${type}</div>
              </div>`
            )
            .addTo(map)
        })

        map.on("mouseenter", "results-circle", () => {
          map.getCanvas().style.cursor = "pointer"
        })
        map.on("mouseleave", "results-circle", () => {
          map.getCanvas().style.cursor = ""
        })
      })

      mapRef.current = map
    }

    init()

    return () => {
      if (mapRef.current) {
        mapRef.current.remove()
        mapRef.current = null
      }
    }
  }, [data])

  // Highlight selected feature
  useEffect(() => {
    if (!mapRef.current || selectedIndex === null) return

    const map = mapRef.current
    const features = data.geojson.features || []

    features.forEach((_, idx) => {
      map.setFeatureState(
        { source: "results", id: idx },
        { selected: idx === selectedIndex }
      )
    })
  }, [selectedIndex, data.geojson.features])

  return (
    <div
      ref={containerRef}
      className="w-full h-full bg-gray-100 relative"
    >
      <div className="absolute top-4 left-4 bg-white px-3 py-2 rounded-lg shadow text-xs text-gray-600 z-10 font-medium">
        🗺️ OpenStreetMap
      </div>
    </div>
  )
}
