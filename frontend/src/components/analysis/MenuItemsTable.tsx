import { MenuItem } from '@/lib/api';

interface MenuItemsTableProps {
  items: MenuItem[];
}

export function MenuItemsTable({ items }: MenuItemsTableProps) {
  if (items.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-4xl mb-2">📋</p>
        <p>No menu items found</p>
      </div>
    );
  }

  // Group by category
  const itemsByCategory = items.reduce((acc, item) => {
    const cat = item.category || 'Uncategorized';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {} as Record<string, MenuItem[]>);

  return (
    <div className="space-y-6">
      {Object.entries(itemsByCategory).map(([category, categoryItems]) => (
        <div key={category}>
          <h4 className="text-md font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              {category}
            </span>
            <span className="text-sm text-gray-500">({categoryItems.length} items)</span>
          </h4>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="text-left py-2 px-3 text-sm font-medium text-gray-600">Item</th>
                  <th className="text-right py-2 px-3 text-sm font-medium text-gray-600">Price</th>
                  <th className="text-left py-2 px-3 text-sm font-medium text-gray-600">Description</th>
                  <th className="text-center py-2 px-3 text-sm font-medium text-gray-600">Source</th>
                </tr>
              </thead>
              <tbody>
                {categoryItems.map((item, idx) => {
                  const itemWithSource = item as MenuItem & { source?: string };
                  return (
                    <tr key={idx} className="border-b hover:bg-gray-50 transition">
                      <td className="py-2 px-3 font-medium text-sm">{item.name}</td>
                      <td className="py-2 px-3 text-right font-mono text-sm">
                        ${item.price?.toFixed(2) || '0.00'}
                      </td>
                      <td className="py-2 px-3 text-gray-600 text-xs max-w-xs truncate">
                        {item.description || '-'}
                      </td>
                      <td className="py-2 px-3 text-center">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          itemWithSource.source === 'sales_data' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-purple-100 text-purple-700'
                        }`}>
                          {itemWithSource.source === 'sales_data' ? '📊 CSV' : '📷 Menu'}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ))}
    </div>
  );
}
