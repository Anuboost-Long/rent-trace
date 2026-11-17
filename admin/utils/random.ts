export type RandomKind = "alphanumeric" | "digits" | "hex" | "fernet";

export const MAX_LENGTH = 256;
export const FERNET_LENGTH = 44;
const FERNET_BITS = 256;

const CHARSETS = {
  alphanumeric:
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
  digits: "0123456789",
  hex: "0123456789abcdef",
};

const randomBytes = (count: number) =>
  crypto.getRandomValues(new Uint8Array(count));

const randomFromCharset = (charset: string, length: number) => {
  const unbiasedLimit = 256 - (256 % charset.length);
  let result = "";
  while (result.length < length) {
    for (const byte of randomBytes(length)) {
      if (byte < unbiasedLimit && result.length < length) {
        result += charset[byte % charset.length];
      }
    }
  }
  return result;
};

const fernetKey = () =>
  btoa(String.fromCharCode(...randomBytes(32)))
    .replaceAll("+", "-")
    .replaceAll("/", "_");

export const generateRandom = (kind: RandomKind, length: number) =>
  kind === "fernet" ? fernetKey() : randomFromCharset(CHARSETS[kind], length);

export const entropyBits = (kind: RandomKind, length: number) =>
  kind === "fernet"
    ? FERNET_BITS
    : Math.round(length * Math.log2(CHARSETS[kind].length));
