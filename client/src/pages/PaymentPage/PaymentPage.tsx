import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useNavigate , useLocation} from 'react-router-dom';
import axios from 'axios';
import { BaseURL } from '@/Constant';

const formSchema = z.object({
    upi: z.string()
        .min(1, { message: 'UPI ID is required' })
        .regex(/[\w.-]+@[\w.-]+/, { message: 'Please enter a valid UPI ID' }), // A basic regex for UPI ID validation
});

const PaymentPage = () => {
    const form = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: {
            upi: "",
        },
    });
    const navigate = useNavigate()

    const location = useLocation();
  const state = location.state as { order: string  , proceed_to_pay : string } ;

  console.log(state?.order , state?.proceed_to_pay);
  

    const onSubmit = (values: z.infer<typeof formSchema>) => {

        console.log(values);
        let data = {
            order_id : state?.order,    
        }
        navigate("/success")
        axios.post(`${BaseURL}payment/` , data)
        .then((res) => {
            console.log(res);
            
        }).catch((err) => {
            console.log(err);
            
        })
    };

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-8'>
                <FormField
                    control={form.control}
                    name="upi"
                    render={({ field, fieldState }) => (
                        <FormItem>
                            <FormLabel>UPI ID</FormLabel>
                            <FormControl>
                                <Input placeholder="Enter your UPI ID" {...field} className="w-full" />
                            </FormControl>
                            <FormMessage>{fieldState.error?.message}</FormMessage>
                        </FormItem>
                    )}
                />
                <Button type="submit" className="w-full mt-6">
                    Proceed to pay Rs. <span>{`  ${state?.proceed_to_pay}`}</span>
                </Button>
            </form>
        </Form>
    );
};

export default PaymentPage;
