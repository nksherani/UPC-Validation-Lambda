export type ExtractResponse = {
  care_labels: Array<Record<string, unknown>>;
  hang_tags: Array<Record<string, unknown>>;
};

const LAMBDA_INVOKE_URL =
  import.meta.env.VITE_LAMBDA_INVOKE_URL ??
  "/lambda/2015-03-31/functions/function/invocations";

const arrayBufferToBase64 = (buffer: ArrayBuffer): string => {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const chunkSize = 0x8000;
  for (let i = 0; i < bytes.length; i += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
  }
  return btoa(binary);
};

export async function extractFiles(files: FileList | File[]): Promise<ExtractResponse> {
  const payloadFiles = await Promise.all(
    Array.from(files).map(async (file) => ({
      filename: file.name,
      content_type: file.type || "application/pdf",
      base64: arrayBufferToBase64(await file.arrayBuffer()),
    }))
  );

  const response = await fetch(LAMBDA_INVOKE_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ files: payloadFiles }),
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  const lambdaResponse = await response.json();
  if (typeof lambdaResponse?.statusCode === "number" && lambdaResponse.statusCode !== 200) {
    throw new Error(lambdaResponse.body ?? "Lambda invocation failed.");
  }
  if (typeof lambdaResponse?.body === "string") {
    return JSON.parse(lambdaResponse.body) as ExtractResponse;
  }
  return lambdaResponse as ExtractResponse;
}
