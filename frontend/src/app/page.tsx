import { getUsersIds } from "@/api/fetch";
import SearchWrapper from "./SearchWrapper";

export default async function Home() {
  const userIdResponse = await getUsersIds();
  console.log(userIdResponse.root.errors)
  const users = userIdResponse.root.children ? userIdResponse.root.children : []

  return <SearchWrapper users={users.map(user => user.fields)}/>
}
