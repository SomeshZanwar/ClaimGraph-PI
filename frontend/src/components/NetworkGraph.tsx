import cytoscape from "cytoscape";
import { useEffect, useRef } from "react";

type GraphPayload = {
  nodes: Array<{ id: string; type: string; label: string }>;
  edges: Array<{ source: string; target: string; type: string }>;
};

export default function NetworkGraph({ data }: { data: GraphPayload }) {
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!ref.current) return;

    const instance = cytoscape({
      container: ref.current,
      elements: [
        ...data.nodes.map((node) => ({
          data: {
            id: node.id,
            label: node.label,
            type: node.type,
          },
        })),
        ...data.edges.map((edge, index) => ({
          data: {
            id: `edge-${index}`,
            source: edge.source,
            target: edge.target,
            type: edge.type,
          },
        })),
      ],
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#6B727A",
            color: "#F2EFE7",
            label: "data(label)",
            "font-size": 10,
            "text-wrap": "ellipsis",
            "text-max-width": 86,
            "text-valign": "bottom",
            "text-margin-y": 7,
            width: 24,
            height: 24,
          },
        },
        {
          selector: 'node[type = "provider"]',
          style: {
            "background-color": "#B76537",
            width: 34,
            height: 34,
          },
        },
        {
          selector: 'node[type = "member"]',
          style: {
            "background-color": "#657B86",
          },
        },
        {
          selector: 'node[type = "claim"]',
          style: {
            "background-color": "#7B806A",
          },
        },
        {
          selector: "edge",
          style: {
            width: 1.5,
            "line-color": "#596068",
            "target-arrow-color": "#596068",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
          },
        },
      ],
      layout: {
        name: "cose",
        animate: false,
        padding: 28,
      },
      minZoom: 0.5,
      maxZoom: 2.5,
    });

    return () => instance.destroy();
  }, [data]);

  return <div ref={ref} className="network-canvas" aria-label="Provider relationship graph" />;
}
