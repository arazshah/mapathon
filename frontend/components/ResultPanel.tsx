"use client";
import { MapPin, Info, List } from "lucide-react";

interface ResultPanelProps {
  response: any;
  onFeatureClick?: (feature: any) => void;
}

export default function ResultPanel({ response, onFeatureClick }: ResultPanelProps) {
  if (!response?.success) {
    return (
      <div className="p-4 text-center text-red-400">
        <Info size={32} className="mx-auto mb-2 opacity-50" />
        <p className="text-sm">{response?.error || "خطا در پردازش درخواست"}</p>
      </div>
    );
  }

  const { answer, map } = response;
  const features = map?.geojson?.features || [];

  return (
    <div className="p-4 space-y-4">
      {/* پاسخ */}
      {answer && (
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
          <div className="flex items-start gap-2">
            <Info size={18} className="text-blue-500 mt-1 flex-shrink-0" />
            <div>
              <h3 className="text-sm font-semibold text-blue-400 mb-2">پاسخ</h3>
              <p className="text-sm text-slate-200 leading-relaxed">{answer}</p>
            </div>
          </div>
        </div>
      )}

      {/* لیست نقاط */}
      {features.length > 0 && (
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700/50">
          <div className="flex items-center gap-2 mb-3">
            <List size={18} className="text-purple-400" />
            <h3 className="text-sm font-semibold text-purple-400">
              لیست نتایج ({features.length} مورد)
            </h3>
          </div>
          <div className="space-y-2 max-h-[500px] overflow-y-auto custom-scrollbar">
            {features.map((feature: any, index: number) => {
              const props = feature.properties || {};
              const coords = feature.geometry?.coordinates;
              const name = props.name || `نتیجه ${index + 1}`;
              const category = props.amenity || props.category || "";
              
              return (
                <div
                  key={index}
                  onClick={() => {
                    if (coords && onFeatureClick) {
                      onFeatureClick(feature);
                    }
                  }}
                  className="bg-slate-900/50 hover:bg-slate-700/50 rounded-lg p-3 cursor-pointer transition-all border border-slate-700/30 hover:border-blue-500/50 group"
                >
                  <div className="flex items-start gap-2">
                    <MapPin 
                      size={16} 
                      className="text-blue-500 mt-1 flex-shrink-0 group-hover:scale-110 transition-transform" 
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate group-hover:text-blue-300">
                        {name}
                      </p>
                      {category && (
                        <p className="text-xs text-slate-400 mt-1">{category}</p>
                      )}
                      {coords && (
                        <p className="text-xs text-slate-600 mt-1 font-mono">
                          {coords[1].toFixed(4)}, {coords[0].toFixed(4)}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
