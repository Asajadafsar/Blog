import * as React from 'react';
import {
    List,
    Datagrid,
    TextField,
    TextInput,
    TopToolbar,
    Pagination,
    SimpleForm,
    required,
    ListProps,
    useListContext,
    ImageField,
    Edit,
    SelectInput,
    ImageInput,
    useGetList,
    useRecordContext,
} from 'react-admin';
import { Stack } from '@mui/material';

const ListToolbar = () => (
    <Stack direction="row" justifyContent="space-between">
        <div></div>
    </Stack>
);

export const PostsList = (props: ListProps<any>) => {
    return (
        <List {...props} filters={<ListToolbar />} pagination={<Pagination rowsPerPageOptions={[10, 25, 50]} />} perPage={10}>
            <Datagrid rowClick="edit">
                <TextField source="id" label="ID" />
                <TextField source="title" label="Title" />
                <ImageField source="image" label="Image" />
                <TextField source="created_at" label="Created At" />
                <TextField source="user.username" label="User" />
                <TextField source="status" label="Status" />
            </Datagrid>
        </List>
    );
};

export const PostEdit = () => {
    // const { data: users, isLoading: usersLoading } = useGetList('users');
    const { data: categories, isLoading: categoriesLoading } = useGetList('category'); // مسیر صحیح برای دسته‌بندی‌ها
    // const userChoices = users?.map(user => ({ id: user.id, name: user.username })) || [];
    const categoryChoices = categories?.map(category => ({ id: category.id, name: category.name })) || [];
    const record = useRecordContext();


    return (
        <Edit>
            <SimpleForm>
                <TextInput source="id" disabled label="ID" />
                <TextInput source="title" validate={required()} label="Title" />
                <TextInput source="content" validate={required()} label="content" />

                <ImageInput source="image" label="Image" accept="image/*">
                    <ImageField source="src" title="title" />
                </ImageInput>
                <TextField source="user.username" label="User" disabled />

                <SelectInput 
                    source="category" 
                    label="Category" 
                    choices={categoryChoices} 
                    isLoading={categoriesLoading}
                />
                <SelectInput 
                    source="status" 
                    label="Status" 
                    choices={[
                        { id: 'active', name: 'active' },
                        { id: 'draft', name: 'draft' },
                    ]}
                />
            </SimpleForm>
        </Edit>
    );
};

export default PostsList;
