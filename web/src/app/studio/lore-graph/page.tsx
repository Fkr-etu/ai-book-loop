"use client";

import React, { useCallback, useMemo } from "react";
import { StudioLayout } from "@/components/StudioLayout";
import { useProjectStore } from "@/lib/useProjectStore";
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Node,
  Edge
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { GitFork, Sparkles, Compass, Users } from "lucide-react";

export default function LoreGraphPage() {
  const { project } = useProjectStore();

  const graphNodesList = project.graphNodes || [];
  const graphEdgesList = project.graphEdges || [];

  // Convert project graphNodes & graphEdges to React Flow format
  const initialNodes: Node[] = useMemo(() => {
    return graphNodesList.map((n, idx) => {
      // Calculate layout positions
      const angle = (idx / (graphNodesList.length || 1)) * 2 * Math.PI;
      const radius = 200;
      const x = 350 + Math.cos(angle) * radius;
      const y = 250 + Math.sin(angle) * radius;

      const isChar = n.type === "character";

      return {
        id: n.id,
        position: { x, y },
        data: { label: n.label, type: n.type },
        style: {
          background: isChar ? "#0b1c30" : "#ffffff",
          color: isChar ? "#ffffff" : "#0b1c30",
          border: isChar ? "2px solid #ffddb8" : "2px solid #0b1c30",
          borderRadius: "8px",
          padding: "10px 14px",
          fontFamily: "Inter, sans-serif",
          fontSize: "12px",
          fontWeight: "600",
          boxShadow: "0 2px 8px rgba(11, 28, 48, 0.08)",
          width: 160,
          textAlign: "center"
        }
      };
    });
  }, [project.graphNodes]);

  const initialEdges: Edge[] = useMemo(() => {
    return graphEdgesList.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.relation,
      animated: true,
      style: { stroke: "#b87500", strokeWidth: 2 },
      labelStyle: { fill: "#2a1700", fontWeight: 600, fontSize: 10 },
      labelBgStyle: { fill: "#ffddb8", fillOpacity: 0.9, rx: 4 }
    }));
  }, [graphEdgesList]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <StudioLayout>
      <div className="flex flex-col h-[calc(100vh-61px)]">
        {/* Graph Header */}
        <div className="p-4 sm:p-6 bg-white border-b border-[#c6c6cd]/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-xs font-mono font-bold text-[#b87500] uppercase tracking-wider flex items-center gap-1">
              <GitFork className="w-3.5 h-3.5" /> Cartographie Narrative Interactive
            </span>
            <h1 className="font-playfair text-xl sm:text-2xl font-bold text-[#0b1c30]">
              Graphe de Relations Lore & Personnages
            </h1>
            <p className="text-xs text-[#45464d] mt-1">
              Visualisez l'écosystème des alliances, rivalités et dépendances canoniques du récit.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 sm:gap-3 text-xs font-mono">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-[#0b1c30] text-[#ffddb8] rounded border border-[#b87500]">
              <Users className="w-3.5 h-3.5" />
              <span>Personnages (Noir)</span>
            </div>
            <div className="flex items-center gap-1.5 px-3 py-1 bg-white text-[#0b1c30] rounded border border-[#0b1c30]">
              <Compass className="w-3.5 h-3.5" />
              <span>Lore / Reliques (Blanc)</span>
            </div>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-[#f8f5f0] relative min-h-[350px]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <Background color="#c6c6cd" gap={16} size={1} />
            <Controls />
          </ReactFlow>
        </div>
      </div>
    </StudioLayout>
  );
}
