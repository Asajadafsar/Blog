/* eslint-disable react/jsx-key */
import * as React from 'react';
import {
    List,
    Datagrid,
    TextField,
    TextInput,
    TopToolbar,
    Pagination,
    Create, 
    SimpleForm, 
    required,
    ListProps,
    useListContext,
    ImageField,
    Edit,
    SelectInput,
    ImageInput,
    Show,
    ShowProps,
    SimpleShowLayout,
    FilterButton,
    FilterForm,
    SearchInput,
} from 'react-admin';
import { Stack } from '@mui/material';


const CustomerFilters = [
    <SearchInput source="username" alwaysOn placeholder="username" />,
  ];
  const ListToolbar = () => (
    <Stack direction="row" justifyContent="space-between">
      <FilterForm filters={CustomerFilters} />
      <div>
        <FilterButton filters={CustomerFilters} />
      </div>
    </Stack>
  );

  
export const UsersList = (props: ListProps<any>) => {
    const { data, ids, total } = useListContext();

    return (
        <List {...props} filters={<ListToolbar />} pagination={<Pagination rowsPerPageOptions={[10, 25, 50]} />} perPage={10}>
            <Datagrid rowClick="edit">
                <TextField source="id" label="ID" />
                <TextField source="username" label="Username" />
                <TextField source="email" label="Email" />
                <TextField source="role" label="Role" />
                <TextField source="phone_number" label="Phone" />
                <TextField source="registration_date" label="Registration Date" />
                <ImageField source="profile_picture" label="Profile Picture" />
            </Datagrid>
        </List>
    );
};

export const UserEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id" disabled label="ID" />
            <TextInput source="username" validate={required()} label="Username" />
            <TextInput source="email" validate={required()} label="Email" />
            <TextInput source="phone_number" label="Phone Number" />
            <SelectInput source="role" label="Role" choices={[
                { id: 'admin', name: 'admin' },
                { id: 'user', name: 'user' },
            ]} />
            <TextInput source="registration_date" disabled label="Registration Date" />
            <ImageInput source="profile_picture" label="Profile Picture" accept="image/*">
                <ImageField source="src" title="title" />
            </ImageInput>
        </SimpleForm>
    </Edit>
);

export const UserShow = (props: ShowProps) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="id" label="ID" />
            <TextField source="username" label="Username" />
            <TextField source="email" label="Email" />
            <TextField source="phone_number" label="Phone Number" />
            <TextField source="role" label="Role" />
            <TextField source="registration_date" label="Registration Date" />
            <ImageField source="profile_picture" label="Profile Picture" />
        </SimpleShowLayout>
    </Show>
);

export default UsersList;