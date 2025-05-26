import axios from "axios";

export async function uploadPDF(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await axios.post(
    `${process.env.NEXT_PUBLIC_BACKEND_URL}/upload`,
    form,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return res.data;
}
