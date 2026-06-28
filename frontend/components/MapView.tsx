"use client";
import { useEffect, useRef, useImperativeHandle, forwardRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

interface MapViewProps {
  response?: any;
  onMarkerClick?: (feature: any) => void;
}

export interface MapViewRef {
  zoomToFeature: (feature: any) => void;
}

const MapView = forwardRef<MapViewRef, MapViewProps>(({ response, onMarkerClick }, ref) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  useImperativeHandle(ref, () => ({
    zoomToFeature: (feature: any) => {
      if (!map.current || !feature) return;
      
      let coords: [number, number] | null = null;
      
      if (feature.geometry?.coordinates) {
        coords = feature.geometry.coordinates;
      } else if (feature.coordinates) {
        coords = feature.coordinates;
      } else if (feature.lat && feature.lon) {
        coords = [feature.lon, feature.lat];
      } else if (feature.lat && feature.lng) {
        coords = [feature.lng, feature.lat];
      } else if (feature.latitude && feature.longitude) {
        coords = [feature.longitude, feature.latitude];
      }
      
      if (coords) {
        map.current.flyTo({
          center: [coords[0], coords[1]],
          zoom: 16,
          duration: 1500,
          essential: true,
        });
      }
    },
  }));

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          "osm-tiles": {
            type: "raster",
            tiles: [
              "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png",
              "https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
              "https://c.tile.openstreetmap.org/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors",
          },
        },
        layers: [
          {
            id: "osm-layer",
            type: "raster",
            source: "osm-tiles",
            minzoom: 0,
            maxzoom: 19,
          },
        ],
      },
      center: [51.389, 35.6892],
      zoom: 11,
    });

    map.current.addControl(new maplibregl.NavigationControl(), "top-left");
    map.current.addControl(new maplibregl.ScaleControl(), "bottom-left");
  }, []);

  useEffect(() => {
    if (!map.current || !response?.success) return;

    markersRef.current.forEach((marker) => marker.remove());
    markersRef.current = [];

    // استخراج نقاط از response.map.geojson.features
    const features = response.map?.geojson?.features || [];
    console.log("Features found:", features.length);

    if (features.length > 0) {
      const bounds = new maplibregl.LngLatBounds();

      features.forEach((feature: any, index: number) => {
        if (feature.geometry?.type !== "Point") return;
        
        const [lng, lat] = feature.geometry.coordinates;
        const props = feature.properties || {};

        const popupContent = document.createElement("div");
        popupContent.className = "marker-popup";
        popupContent.innerHTML = `
          <div class="marker-popup-title">${props.name || `نتیجه ${index + 1}`}</div>
          ${props.amenity ? `<div class="marker-popup-content">نوع: ${props.amenity}</div>` : ""}
          <div class="marker-popup-coords">${lat.toFixed(6)}, ${lng.toFixed(6)}</div>
        `;

        const popup = new maplibregl.Popup({
          offset: 25,
          closeButton: true,
          closeOnClick: true,
          maxWidth: "300px",
        }).setDOMContent(popupContent);

        const marker = new maplibregl.Marker({
          color: "#3b82f6",
          scale: 1.2,
        })
          .setLngLat([lng, lat])
          .setPopup(popup)
          .addTo(map.current!);

        marker.getElement().addEventListener("click", () => {
          if (onMarkerClick) {
            onMarkerClick(feature);
          }
        });

        markersRef.current.push(marker);
        bounds.extend([lng, lat]);
      });

      if (!bounds.isEmpty()) {
        map.current.fitBounds(bounds, {
          padding: { top: 50, bottom: 50, left: 50, right: 50 },
          maxZoom: 16,
        });
      }
    }
  }, [response, onMarkerClick]);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
});

MapView.displayName = "MapView";
export default MapView;
