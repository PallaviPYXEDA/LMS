import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { Amplify } from 'aws-amplify';
import { awsIdentityConfig } from '../../aws-exports';


Amplify.configure(awsIdentityConfig);

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}
