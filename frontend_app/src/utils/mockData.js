export const mockConversations = [
  {
    id: '1',
    title: 'Food Spending Analysis',
    timestamp: '2025-01-18T10:30:00',
    csvStatus: 'active',
    csvExpiry: '2025-01-25T10:30:00',
    csvFilename: 'transactions.csv'
  },
  {
    id: '2',
    title: 'Q4 Sales Report',
    timestamp: '2025-01-17T15:20:00',
    csvStatus: 'expired',
    csvExpiry: '2025-01-10T15:20:00',
    csvFilename: 'sales_q4.csv'
  },
  {
    id: '3',
    title: 'Customer Demographics',
    timestamp: '2025-01-16T09:00:00',
    csvStatus: 'active',
    csvExpiry: '2025-01-23T09:00:00',
    csvFilename: 'customers.csv'
  }
];

export const mockMessages = {
  '1': [
    {
      id: 'm1',
      role: 'user',
      content: 'How much did I spend on food last month?',
      timestamp: '2025-01-18T10:31:00'
    },
    {
      id: 'm2',
      role: 'assistant',
      content: 'You spent ₹33,468.31 on food last month.',
      timestamp: '2025-01-18T10:31:05',
      cost: 0.0012
    },
    {
      id: 'm3',
      role: 'user',
      content: 'Show me a chart of spending by category',
      timestamp: '2025-01-18T10:32:00'
    },
    {
      id: 'm4',
      role: 'assistant',
      content: 'Here is your spending breakdown by category',
      timestamp: '2025-01-18T10:32:10',
      cost: 0.0024,
      hasPlot: true
    }
  ],
  '2': [
    {
      id: 'm5',
      role: 'user',
      content: 'What were the top selling products?',
      timestamp: '2025-01-17T15:21:00'
    },
    {
      id: 'm6',
      role: 'assistant',
      content: 'The top 3 selling products were: Product A ($12,450), Product B ($9,230), and Product C ($7,890).',
      timestamp: '2025-01-17T15:21:08',
      cost: 0.0015
    }
  ],
  '3': []
};
