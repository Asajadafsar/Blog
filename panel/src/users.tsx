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
    ImageField
} from 'react-admin';
import { Stack } from '@mui/material';

const UserFilters = [
    <SearchInput source="username" alwaysOn />,
    <TextInput label="username" source="username" resettable />
];

const ListToolbar = () => (
    <Stack direction="row" justifyContent="space-between">
        <FilterForm filters={UserFilters} />
        <div>
            <FilterButton filters={UserFilters} />
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

export default UsersList;
