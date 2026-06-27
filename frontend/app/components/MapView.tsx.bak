"use client";

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

interface MapViewProps {
  geojson?: any;
  mapRef?: React.MutableRefObject<any>;
}

export default function MapView({ geojson, mapRef }: MapViewProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const localMapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            // ✅ tiles array - نه url
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap",
          },
        },
        layers: [
          {
            id: "osm",
            type: "raster",
            source: "osm",
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [51.3895, 35.6892],
      zoom: 10,
    });

    map.addControl(new maplibregl.NavigationControl(), "bottom-right");

    localMapRef.current = map;
    if (mapRef) mapRef.current = map;

    map.on("load", () => {
      if (geojson) addGeoJSON(map, geojson);
    });

    return () => map.remove();
  }, []);

  useEffect(() => {
    if (localMapRef.current && geojson) {
      addGeoJSON(localMapRef.current, geojson);
    }
  }, [geojson]);

  const addGeoJSON = (map: maplibregl.Map, data: any) => {
    if (map.getLayer("geojson-layer")) map.removeLayer("geojson-layer");
    if (map.getSource("geojson-source")) map.removeSource("geojson-source");

    map.addSource("geojson-source", { type: "geojson", data });

    map.addLayer({
      id: "geojson-layer",
      type: "circle",
      source: "geojson-source",
      paint: {
        "circle-radius": 7,
        "circle-color": "#2563eb",
        "circle-stroke-width": 2,
        "circle-stroke-color": "#ffffff",
        "circle-opacity": 0.9,
      },
    });

    map.on("click", "geojson-layer", (e: any) => {
      const feature = e.features?.[0];
      if (!feature) return;
      let coords: [number, number] = [0, 0];
      if (feature.geometry.type === "Point") {
        coords = feature.geometry.coordinates as [number, number];
      } else if (feature.geometry.coordinates) {
        const first = feature.geometry.coordinates[0];
        coords = Array.isArray(first[0]) ? first[0] : first;
      }
      new maplibregl.Popup()
        .setLngLat(coords)
        .setHTML(`<div style="padding:4px;">
          <p style="font-weight:bold;margin:0;">${feature.properties?.name || "نامشخص"}</p>
          <p style="color:#64748b;font-size:12px;margin:2px 0 0;">${feature.properties?.type || ""}</p>
        </div>`)
        .addTo(map);
    });

    map.on("mouseenter", "geojson-layer", () => {
      map.getCanvas().style.cursor = "pointer";
    });
    map.on("mouseleave", "geojson-layer", () => {
      map.getCanvas().style.cursor = "";
    });
  };

  return <div ref={containerRef} className="w-full h-full" />;
}
