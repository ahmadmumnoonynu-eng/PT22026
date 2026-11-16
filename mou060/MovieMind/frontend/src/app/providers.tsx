import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState, type PropsWithChildren } from "react";

import { App } from "@/app/App";
import { authSession } from "@/lib/auth/session";
import { isUserSpecificQuery } from "@/lib/query/keys";

function QueryProvider({ children }: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  useEffect(
    () =>
      authSession.subscribe((token) => {
        if (token === null) {
          queryClient.removeQueries({
            predicate: (query) => isUserSpecificQuery(query.queryKey),
          });
        }
      }),
    [queryClient],
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

export function AppProviders() {
  return (
    <QueryProvider>
      <App />
    </QueryProvider>
  );
}
