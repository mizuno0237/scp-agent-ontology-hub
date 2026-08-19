export type ObjectType = {
  id: string;
  description: string;
  primaryKey: string;
  properties: { name: string; type: string }[];
};

export type LinkType = {
  id: string;
  from: string;
  to: string;
  cardinality: string;
  description: string;
};

export type LogicRule = {
  id: string;
  kind: string;
  text: string;
  agentMust?: string;
};

export type ActionDef = {
  id: string;
  objectType: string;
  description: string;
  humanInTheLoop: boolean;
};

export type OntologySchema = {
  objectTypes: { objectTypes: ObjectType[] };
  linkTypes: { linkTypes: LinkType[] };
  logicRules: { rules: LogicRule[] };
  actions: { actions: ActionDef[] };
};

export type GraphPayload = {
  domain: string;
  synthetic: boolean;
  instances: {
    Supplier: { id: string; name: string; tier: string; region: string }[];
    PurchaseOrder: { order_id: string; order_date: string; status: string; amount: number }[];
    OrderLine: {
      id: string;
      order_id: string;
      sku: string;
      name: string;
      quantity: number;
      unit_price: number;
      material_class: string;
    }[];
    Shipment: {
      order_id: string;
      carrier: string;
      expected_days: number | null;
      actual_days: number | null;
      on_time: boolean | null;
    }[];
    InventoryPolicy: {
      material_class: string;
      safety_stock: number;
      reorder_point: number;
      max_stock: number;
      on_hand: number;
    }[];
  };
  links: {
    type: string;
    fromType: string;
    from: string;
    toType: string;
    to: string;
  }[];
};

export type ActionPreview = {
  actionId: string;
  objectId?: string;
  allowed: boolean;
  humanInTheLoop: boolean;
  reason: string;
  firedRules: string[];
};

export type ObjectLookup = {
  objectType: string;
  primaryKey: string;
  synthetic: boolean;
  object: Record<string, string | number | boolean | null>;
  links: GraphPayload["links"];
};

export type WalkPayload = {
  objectType: string;
  objectId: string;
  linkType: string;
  synthetic: boolean;
  object: Record<string, string | number | boolean | null>;
  neighbors: {
    objectType: string;
    object: Record<string, string | number | boolean | null>;
    via: GraphPayload["links"][number];
  }[];
};

export const TYPE_STAMP: Record<string, string> = {
  Supplier: "SUP",
  PurchaseOrder: "PO",
  OrderLine: "LIN",
  InventoryPolicy: "POL",
  Shipment: "SHP",
};
