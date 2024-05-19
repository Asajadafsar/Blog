import {
  Admin,
  Resource,
  ListGuesser,
  EditGuesser,
  ShowGuesser,
} from "react-admin";
import { UserCreate } from "./UserCreate";
import  dataProvider  from "./dataProvider";
import { authProvider } from "./authProvider";
import { UsersList,UserEdit,UserShow } from "./users";
import { LogList } from "./logs";
import { PostsList,PostEdit } from "./posts";
import { CommentList } from "./comment";
import { CategoriesList,CategoryEdit } from "./category";
import CategoryCreate from "./CategoryCreate";
import { TagList, TagEdit } from './tag';

export const App = () => (
  <Admin dataProvider={dataProvider} authProvider={authProvider}>
    <Resource
      name="users"
      list={UsersList}
      edit={UserEdit}
      show={UserShow}
      create={UserCreate}
    />
    <Resource
      name="logs"
      list={LogList} 
      show={ShowGuesser}
    />
    <Resource
      name="posts"
      list={PostsList}
      edit={PostEdit}
    />
    <Resource
      name="comment"
      list={CommentList}
    />
    <Resource
      name="tag"
      list={TagList}
      edit={TagEdit}
    />
    <Resource
      name="category"
      list={CategoriesList}
      edit={CategoryEdit}
      create={CategoryCreate}

    />
  </Admin>
);
