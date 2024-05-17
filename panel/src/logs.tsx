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
    </Stack>
);

export const LogList = (props: ListProps<any>) => {
    const { data, ids, total } = useListContext();

    return (
        <List {...props} filters={<ListToolbar />} pagination={<Pagination rowsPerPageOptions={[10, 25, 50]} />} perPage={10}>
            <Datagrid rowClick="edit">
                <TextField source="id" label="ID" />
                <TextField source="action" label="action" />
                <TextField source="ip_address" label="ip address" />
                <TextField source="action_date" label="action Date" />
                <DeleteButton basePath="/logs" />
            </Datagrid>
        </List>
    );
};

export default LogList;
