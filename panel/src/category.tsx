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
} from 'react-admin';
import { Stack } from '@mui/material';

const ListToolbar = () => (
    <Stack direction="row" justifyContent="space-between">
        <div>
        </div>
    </Stack>
);

export const CategoriesList = (props: ListProps<any>) => {
    const { data, ids, total } = useListContext();

    return (
        <List {...props} filters={<ListToolbar />} pagination={<Pagination rowsPerPageOptions={[10, 25, 50]} />} perPage={10}>
            <Datagrid rowClick="edit">
                <TextField source="id" label="ID" />
                <TextField source="name" label="Name" />
            </Datagrid>
        </List>
    );
};

export const CategoryEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="id" disabled label="ID" />
            <TextInput source="name" validate={required()} label="Name" />
        </SimpleForm>
    </Edit>
);

export default CategoriesList;
