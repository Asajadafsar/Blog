import * as React from 'react';
import {
    List,
    Datagrid,
    TextField,
    TextInput,
    SearchInput,
    TopToolbar,
    CreateButton,
    Pagination,
    FilterButton,
    Create, 
    SimpleForm, 
    FilterForm,
    required,
    ListProps,
    useListContext,
    ImageField,
    EditButton,
    DeleteButton
} from 'react-admin';
import { Stack } from '@mui/material';

const ListToolbar = () => (
    <Stack direction="row" justifyContent="space-between">
        {/* Additional actions can be added here */}
    </Stack>
);

export const CommentList = (props: ListProps<any>) => {
    const { data, ids, total } = useListContext();

    return (
        <List {...props} filters={<ListToolbar />} pagination={<Pagination rowsPerPageOptions={[10, 25, 50]} />} perPage={10}>
            <Datagrid rowClick="edit">
                <TextField source="id" label="ID" />
                <TextField source="content" label="Content" />
                <TextField source="created_at" label="Created At" />
                <TextField source="updated_at" label="Updated At" />
                <TextField source="user_id" label="User ID" />
                <TextField source="post_id" label="Post ID" />
                <DeleteButton basePath="/comments" />
            </Datagrid>
        </List>
    );
};

export default CommentList;
