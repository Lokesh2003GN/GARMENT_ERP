from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.db.models import Max
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.http import JsonResponse

User = get_user_model()

def custom_404_view(request, exception):
    return redirect('home')

@login_required
def home(request):
    user = request.user
    if user.is_owner:
        return redirect('owner_dashboard')
    elif user.is_weaver :
        auth_login(request, user)
        return redirect('weaver_dashboard')
    elif user.is_warper:
        auth_login(request, user)
        return redirect('warper_dashboard')
    else:
        messages.error(request, "User profile not associated with owner or staff.")
        return redirect('user_login')
	
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_owner:
                auth_login(request, user)
                return redirect('owner_dashboard')
            elif user.is_weaver:
                auth_login(request, user)
                return redirect('weaver_dashboard')
            elif user.is_warper :
                auth_login(request, user)
                return redirect('warper_dashboard')
            else:
                messages.error(request, "User type is not recognized.")
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'core/login.html')
    

def register_owner(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        company_name = request.POST['company_name']
        company_address = request.POST['company_address']
        phone1 = request.POST['phone1']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return redirect('register_owner')

        user = User.objects.create_user( username=username,
        password=password,
        type='owner',
        phone1=phone1
        )
        company = Company.objects.create(owner=user, name=company_name, address=company_address)

        auth_login(request, user)  
        messages.success(request, "Registration successful!")
        return redirect('owner_dashboard')  

    return render(request, 'core/register.html')

@login_required
def account(request):
    return render(request, 'core/account.html')

@login_required
def edit_account(request):
    user = request.user  # CustomUser

    if request.method == 'POST':
        new_username = request.POST.get('name')
        new_email = request.POST.get('email')
        new_phone1 = request.POST.get('phone1')
        new_phone2 = request.POST.get('phone2')
        new_address = request.POST.get('address')

        # Check if username is taken by another user
        if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
            messages.error(request, 'Username already exists. Please choose another one.')
            return render(request, 'note/account.html', {'user': user})

        user.username = new_username
        user.email = new_email
        user.phone1 = new_phone1
        user.phone2 = new_phone2
        user.address = new_address

        user.save()
        messages.success(request, 'Account updated successfully.')
        return redirect('edit_account')

    return render(request, 'core/account.html', {'user': user})  

@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('account')  # or wherever your profile page is

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('account')

        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return redirect('account')

        # Set the new password
        user.set_password(new_password)
        user.save()

        # Keep the user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Your password has been updated successfully.")
        return redirect('account')  # Adjust as needed

    return redirect('account')
	
@user_passes_test(lambda u: u.is_owner)
def owner_dashboard(request):
    return render(request, 'core/owner_dashboard.html')

@user_passes_test(lambda u: u.is_weaver)
def weaver_dashboard(request):
    return render(request, 'core/weaver_dashboard.html')
@user_passes_test(lambda u: u.is_warper)
def warper_dashboard(request):
    return render(request, 'core/warper_dashboard.html')
    


@user_passes_test(lambda u: u.is_owner)
def staff_management(request):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']
        phone1 = request.POST['phone1']
        address = request.POST['address']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        else:
            staff_user = User.objects.create_user(
                username=username,
                password=password,
                type='staff',
                phone1=phone1,
                address = address
            )
            Staff.objects.create(user=staff_user, company=company, role=role)
            messages.success(request, f"Staff {username} added successfully.")

        return redirect('staff_management')

    staff_members = Staff.objects.filter(company=company).select_related('user')
    
    context = {
        'staff_members': staff_members,
        'company': company,
    }
    return render(request, 'core/staff.html', context)
    
@user_passes_test(lambda u: u.is_owner)
def add_new_warp_design(request):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)
    if request.method == 'POST':
        name = request.POST.get('name')
        warp = WarpDesign.objects.create(name=name, company=company)

        yarn_ids = request.POST.getlist('yarn_id[]')
        lint_counts = request.POST.getlist('lint[]')
        colors = request.POST.getlist('color[]')
        i=1
        for yarn_id, lint, color in zip(yarn_ids, lint_counts, colors):
            WarpDesignEntry.objects.create(
                order = i,
                warp_design=warp,
                yarn_id=int(yarn_id),
                lint_count=float(lint),
                color=color
            )
            i+=1
        return redirect('warp_design_list')
    yarns = Yarn.objects.filter(company=company)
    return render(request, 'core/add_new_warp_design.html',{
        'yarns': yarns,
    })

@user_passes_test(lambda u: u.is_owner)
def edit_warp_design(request, warp_id):
    warp = get_object_or_404(WarpDesign, id=warp_id, company__owner=request.user)
    yarns = Yarn.objects.filter(company=warp.company)

    if request.method == 'POST':
        # Update warp name
        if 'delete_warp' in request.POST:
            warp.delete()
            return redirect('warp_design_list')

        warp.name = request.POST.get('name')
        warp.save()

        # Clear existing entries
        warp.entries.all().delete()

        # Recreate entries from POST
        yarn_ids = request.POST.getlist('yarn_id[]')
        lint_counts = request.POST.getlist('lint[]')
        colors = request.POST.getlist('color[]')

        for i, (yarn_id, lint, color) in enumerate(zip(yarn_ids, lint_counts, colors), start=1):
            WarpDesignEntry.objects.create(
                order=i,
                warp_design=warp,
                yarn_id=int(yarn_id),
                lint_count=float(lint),
                color=color
            )

        return redirect('warp_design_list')  
    return render(request, 'core/edit_warp_design.html', {
        'warp': warp,
        'entries': warp.entries.all().order_by('order'),
        'yarns': yarns,
    })
@user_passes_test(lambda u: u.is_owner)
def warp_design_list(request):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)
    warp_designs = WarpDesign.objects.filter(company=company)

    for warp in warp_designs:
        warp_entries = WarpDesignEntry.objects.filter(warp_design=warp)
        entry_dict = {entry.order: entry for entry in warp_entries}

        warp.total_lint = sum(entry.lint_count for entry in warp.entries.all())
        warp.entry_dict = {entry.order: entry for entry in warp.entries.all()}


    return render(request, 'core/warp_design_list.html', {
        'warp_designs': warp_designs,
    })

    

@user_passes_test(lambda u: u.is_owner)
def warp_management(request):
    return render(request, 'core/warp_management.html')

@user_passes_test(lambda u: u.is_owner)
def piece_management(request):
    return render(request, 'core/piece_management.html')

@user_passes_test(lambda u: u.is_owner)
def assign_weaver(request, warp_id):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)

    if request.method == 'POST':
        weaver_id = request.POST.get('weaver_select')

        warp = get_object_or_404(Warp, id=warp_id)
        weaver = get_object_or_404(CustomUser, id=weaver_id)

        warp.weaver = weaver
        warp.date_start_weaver = request.POST.get('date_start_weaver')
        warp.length = request.POST.get('length')
        warp.save()

        Wage.objects.create(
            warp=warp,
            date=timezone.now().date(),
            wage_good=request.POST.get('wage_good'),
            wage_demage=request.POST.get('wage_demage'),
            wage_extra=request.POST.get('wage_extra')
        )

        messages.success(request, "Weaver assigned successfully.")
        return redirect('warp_list')

    # GET request – show the form
    weavers = Staff.objects.filter(company=company, role='weaver').select_related('user')
    warp = get_object_or_404(Warp, id=warp_id)
    return render(request, 'core/assign_weaver.html', {
        'weavers': weavers
    })

      
@user_passes_test(lambda u: u.is_owner)
def make_warp(request):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)
    print("assign_weaver view accessed via", request.method)
    if request.method == 'POST':
        warp_id = request.POST.get('warp_design_select')
        design =get_object_or_404(WarpDesign,id=warp_id)
        warper_id = request.POST.get('warper_select')
        warper = get_object_or_404(CustomUser, id=warper_id)
        name = request.POST.get('name')
        meters = request.POST.get('meters')
        warp_wage = request.POST.get('warp_wage')
        date_start_warper = request.POST.get('date_start_warper')
        warp_yarn = request.POST.get('warp_yarn')
        isComplected = False
        isWarped = False
        isSecondary =False
        Warp.objects.create(
            design = design,
            warper=warper,
            name=name,
            meters=meters,
            date_start_warper=date_start_warper,
            warp_wage =warp_wage,
            warp_yarn = warp_yarn,
            isComplected=isComplected,
            isWarped = isWarped,
            isSecondary = isSecondary
        )


        messages.success(request, "Warp created successfully.")
        return redirect('warp_list')
    warpers = Staff.objects.filter(company=company).select_related('user').filter(role='warper')
    designs = WarpDesign.objects.filter(company=company)
    return render(request, 'core/make_warp.html', {
        'warpers':warpers,
        'designs': designs
    })


@require_POST
@user_passes_test(lambda u: u.is_owner)
def complete_warping(request, warp_id):
    warp = get_object_or_404(Warp, id=warp_id)
    warp.isWarped = True
    warp.save()
    messages.success(request, "Warping marked as completed.")
    return redirect('warp_list')


@require_POST
@user_passes_test(lambda u: u.is_owner)
def complete_weaving(request, warp_id):
    warp = get_object_or_404(Warp, id=warp_id)
    warp.isComplected = True
    warp.save()
    messages.success(request, "Weaving marked as completed.")
    return redirect('warp_list')

@user_passes_test(lambda u: u.is_owner)
def warp_list(request):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)

    not_warped = Warp.objects.filter(isWarped=False, design__company=company)
    warped_not_weaving = Warp.objects.filter(isWarped=True, weaver__isnull=True, design__company=company)
    in_weaving = Warp.objects.filter(isWarped=True, weaver__isnull=False, isComplected=False, design__company=company)
    completed_warps = Warp.objects.filter(isComplected=True, design__company=company)

    weavers = Staff.objects.filter(company=company, role='weaver').select_related('user')

    context = {
        'not_warped': not_warped,
        'warped_not_weaving': warped_not_weaving,
        'in_weaving': in_weaving,
        'completed_warps': completed_warps,
        'weavers': weavers,
    }
    return render(request, 'core/warp_list.html', context)

@user_passes_test(lambda u: u.is_warper)
def warp_list_warper(request):
    owner = request.user.staff.company.owner
    company = get_object_or_404(Company, owner=owner)
    warpes = Warp.objects.filter(design__company=company, warper=request.user)
    return render(request, 'core/warp_list_warper.html', {'warpes': warpes})

@user_passes_test(lambda u: u.is_owner)
def edit_warp(request, warp_id):
    owner = request.user
    company = get_object_or_404(Company, owner=owner)
    warp = get_object_or_404(Warp, id=warp_id, design__company=company)

    if request.method == 'POST':
        if 'delete_warp' in request.POST:
            warp.delete()
            messages.success(request, "Warp deleted successfully.")
            return redirect('warp_wise')

        design_id = request.POST.get('warp_design_select')
        warp.design = get_object_or_404(WarpDesign, id=design_id)

        weaver_id = request.POST.get('weaver_select')
        warper_id = request.POST.get('warper_select')
        warp.weaver = get_object_or_404(CustomUser, id=weaver_id) if weaver_id else None
        warp.warper = get_object_or_404(CustomUser, id=warper_id) if warper_id else None

        warp.name = request.POST.get('name')
        warp.meters = request.POST.get('meters') or 0
        warp.date_start_warper = request.POST.get('date_start_warper') or None
        warp.date_start_weaver = request.POST.get('date_start_weaver') or None
        warp.length = request.POST.get('length') or 0
        warp.warp_wage = request.POST.get('warp_wage') or 0

        warp.isComplected = 'isComplected' in request.POST
        warp.isWarped = 'isWarped' in request.POST
        warp.isSecondary = 'isSecondary' in request.POST  
       
        warp.save() 

        if not warp.isSecondary:
            selected_ids = request.POST.getlist('secondary_warps')
            warp.secondary_warps.exclude(id__in=selected_ids).update(primary_warp=None)
            Warp.objects.filter(id__in=selected_ids).update(primary_warp=warp)

        messages.success(request, "Warp updated successfully.")
        return redirect('warp_list') 


    weavers = Staff.objects.filter(company=company, role='weaver').select_related('user')
    warpers = Staff.objects.filter(company=company, role='warper').select_related('user')
    warp_designs = WarpDesign.objects.filter(company=company)
    wages = Wage.objects.filter(warp=warp)

    potential_secondaries = Warp.objects.filter(
        Q(primary_warp__isnull=True) | Q(primary_warp=warp),
        design__company=company
    ).exclude(id=warp.id)

    context = {
        'warp': warp,
        'wage_list': wages,
        'weavers': weavers,
        'warpers': warpers,
        'warp_designs': warp_designs,
        'all_warps': potential_secondaries,
    }
    return render(request, 'core/edit_warp.html', context)



@user_passes_test(lambda u: u.is_owner)
@require_POST
def make_secondary(request, warp_id):
    try:
        warp = Warp.objects.get(id=warp_id, design__company__owner=request.user)
        warp.isSecondary = True
        warp.save()
        return JsonResponse({'status': 'success'})
    except Warp.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Warp not found'}, status=404)


@require_POST
@user_passes_test(lambda u: u.is_owner)
def edit_wage(request, warp_id):
    owner = request.user
    warp = get_object_or_404(Warp, id=warp_id)

    # Delete old wages before adding new
    Wage.objects.filter(warp=warp).delete()

    dates = request.POST.getlist('date[]')
    goods = request.POST.getlist('wage_good[]')
    demages = request.POST.getlist('wage_demage[]')
    extras = request.POST.getlist('wage_extra[]')

    for d, g, dm, ex in zip(dates, goods, demages, extras):
        if d:  # Avoid empty date
            Wage.objects.create(
                warp=warp,
                date=d,
                wage_good=g or 0,
                wage_demage=dm or 0,
                wage_extra=ex or 0
            )

    return redirect('edit_warp', warp_id=warp.id)

@csrf_exempt
@user_passes_test(lambda u: u.is_owner)
def add_piece(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        warp_ids = request.POST.getlist('warp_id[]')
        counts = request.POST.getlist('count[]')
        lengths = request.POST.getlist('length[]')
        types = request.POST.getlist('type[]')

        piece_date = parse_date(date)

        for warp_id, count, piece_type, length in zip(warp_ids, counts, types, lengths):
            count = float(count)
            length = float(length)
            try:
                warp = Warp.objects.get(id=warp_id)
            except Warp.DoesNotExist:
                continue

            wage = Wage.objects.filter(warp=warp.id, date__lte=piece_date).order_by('-date', '-id').first()
            if not wage:
                continue

            Piece.objects.create(
                date=piece_date,
                warp=warp,
                count=count,
                type=piece_type,
                length=length
            )
        return redirect('home')
    company = get_object_or_404(Company, owner=request.user)
    weavers = Staff.objects.filter(company=company).select_related('user').filter(role='weaver')
    warp_list = Warp.objects.filter(design__company=company, isWarped = True, isComplected = False).exclude(isSecondary=True)
    return render(request, 'core/add_piece.html', {'warp_list': warp_list, 'weavers': weavers})
    
@user_passes_test(lambda u: u.is_owner)
def edit_piece(request, piece_id):
    piece = get_object_or_404(Piece, id=piece_id)
    company = get_object_or_404(Company, owner=request.user)
    weavers = Staff.objects.filter(company=company).select_related('user').filter(role='weaver')    
    if request.method == 'POST':
        if 'delete' in request.POST:
            piece.delete()
            return redirect('date_wise')
        else:
            piece.date = request.POST.get('date')
            piece.count = request.POST.get('count')
            piece.type = request.POST.get('type')
            warp_id = request.POST.get('warp_id')
            piece.length = request.POST.get('length')
            piece.warp_id = get_object_or_404(Warp, id=warp_id)
            piece.save()
            return redirect('date_wise')

    
	
    return render(request, 'core/edit_piece.html', {
        'piece': piece,
        'warp_list': Warp.objects.all(),
        'weavers': weavers
    })
    
    

@login_required
def date_wise(request):
    try:
        if request.user.staff.role == 'weaver':
            selected_weaver = request.user
            weaver_id = selected_weaver.id
            owner = selected_weaver.staff.company.owner
    except:
        weaver_id = request.GET.get('weaver_id')
        selected_weaver = CustomUser.objects.filter(id=weaver_id).first()
        owner = request.user
    
    grouped_by_date = {}
    company = get_object_or_404(Company, owner=owner)
    weavers = Staff.objects.filter(company=company, role='weaver').select_related('user')

    if weaver_id:
        try:
            selected_weaver = CustomUser.objects.get(id=weaver_id)
            pieces = Piece.objects.filter(warp__weaver=selected_weaver).order_by('-date')

            grouped = defaultdict(list)

            for piece in pieces:
                wage = Wage.objects.filter(warp=piece.warp, date__lte=piece.date).order_by('-date', '-id').first()
                if not wage:
                    continue

                # Determine rate based on piece type
                if piece.type == 'good':
                    rate = wage.wage_good
                elif piece.type == 'demage':
                    rate = wage.wage_demage
                elif piece.type == 'extra':
                    rate = wage.wage_extra
                else:
                    rate = wage.wage_good

                # Handle return case
                count = -piece.count if piece.type == 'return' else piece.count

                # Calculate meter and amount
                meter = round(count * piece.length, 2)
                amount = round(rate * meter, 2)

                # Attach additional data to each piece (temporarily)
                piece.calculated_meter = meter
                piece.calculated_amount = amount
                piece.wage = rate

                grouped[piece.date].append(piece)

            grouped_by_date = dict(sorted(grouped.items(), reverse=True))


        except CustomUser.DoesNotExist:
            selected_weaver = None

    return render(request, 'core/date_wise.html', {
        'weavers': weavers,
        'selected_weaver': selected_weaver,
        'grouped_by_date': grouped_by_date,
    })
    
    
    
    
@login_required
def warp_wise(request):
    try:
        if request.user.staff.role == 'weaver':
            selected_weaver = request.user
            weaver_id = selected_weaver.id
            owner = selected_weaver.staff.company.owner
    
    except:
        weaver_id = request.GET.get('weaver_id')
        selected_weaver = CustomUser.objects.filter(id=weaver_id).first()
        owner = request.user
        
    grouped_pieces = defaultdict(list)
    totals = {}
    warp_map = {}

    company = get_object_or_404(Company, owner=owner)
    weavers = Staff.objects.filter(company=company, role='weaver').select_related('user')

    if weaver_id:
        try:
            selected_weaver = CustomUser.objects.get(id=weaver_id)
            warp_list = Warp.objects.filter(weaver=selected_weaver)

            for warp in warp_list:
                if warp.isSecondary:
                    continue
                pieces = Piece.objects.filter(warp=warp).order_by('date')
                wage = Wage.objects.filter(warp=warp).order_by('-date', '-id').first()
                warp_map[warp.id] = warp
                if warp.meters:
                    total_count = int(round(warp.meters / warp.length, 0)) if warp.length else 0
                else :
                    total_count=0
                total_meter = round(total_count * warp.length, 2) if warp.length else 0

                totals[warp.id] = {
                    "total_peace": total_count,
                    "total_meter": total_meter,
                    "latest_wage": wage.wage_good if wage else 0,
                }

                for piece in pieces:
                    wage_piece = Wage.objects.filter(warp=warp, date__lte=piece.date).order_by('-date', '-id').first()
                    if not wage_piece:
                        continue

                    if piece.type == 'good':
                        rate = wage_piece.wage_good
                        count = piece.count
                    elif piece.type == 'demage':
                        rate = wage_piece.wage_demage
                        count = piece.count
                    elif piece.type == 'extra':
                        rate = wage_piece.wage_extra
                        count = piece.count
                    else:  # return
                        rate = wage_piece.wage_good
                        count = -piece.count

                    meter = round(count * piece.length, 2)
                    amount = round(rate * meter, 2)

                    # Attach temporary values
                    piece.calculated_meter = meter
                    piece.calculated_amount = amount
                    piece.wage = rate

                    grouped_pieces[warp.id].append(piece)

        except CustomUser.DoesNotExist:
            selected_weaver = None

    return render(request, "core/warp_wise.html", {
        'weavers': weavers,
        'selected_weaver': selected_weaver,
        "grouped_pieces": dict(grouped_pieces),
        "totals": totals,
        "warp_map": warp_map
    })
    
    
    
@user_passes_test(lambda u: u.is_owner)
def add_wage(request):
    company = get_object_or_404(Company, owner=request.user)
    if request.method == 'POST':
        date = request.POST.get('date')
        staff = request.POST.get('staff_select')
        amount = request.POST.get('amount')
        note = request.POST.get('note')
        if not staff:
            company = get_object_or_404(Company, owner=request.user)
            return render(request, 'core/add_wage.html', {
                "staff": Staff.objects.filter(company=company),
                "error": "Please select a staff."
            })

        Transactions.objects.create(
            date=date,
            staff=CustomUser.objects.get(id=staff),
            amount=amount,
            note = note,
            company=company
        )
        return redirect('transactions')
    staff = Staff.objects.filter(company=company)
    return render(request, 'core/add_wage.html', {"staff": staff })
    
    
@login_required
def change_wage(request, id):
    wage = get_object_or_404(Transactions, id=id)
    if request.method == "POST":
        if 'delete_wage' in request.POST:
            wage.delete()
            return redirect('transactions')
        
        wage.date = request.POST.get('date')
        wage.note = request.POST.get('note')
        wage.amount = request.POST.get('amount')
        staff = request.POST.get('staff_select')
        wage.staff = CustomUser.objects.get(id=staff)
        wage.save()
        return redirect('transactions')
    
    company = get_object_or_404(Company, owner=request.user)
    staff = Staff.objects.filter(company=company)
    return render(request, 'core/change_wage.html', {
        'wage': wage,
        'staff': staff
    })
    
    

@login_required
def transactions(request):
    try:
        if request.user.staff.role in ['weaver', 'warper']:
            selected_staff = request.user
            staff_id = selected_staff.id
            role = request.user.staff.role
            owner = selected_staff.staff.company.owner
        else:
            raise Exception
    except:
        staff_id = request.GET.get('weaver_id')  # can be warper or weaver
        selected_staff = CustomUser.objects.filter(id=staff_id).first()
        role = selected_staff.staff.role if selected_staff and hasattr(selected_staff, 'staff') else None
        owner = request.user

    combined_data = []

    # Credit Transactions (same for both weaver and warper)
    credit_trans = Transactions.objects.select_related('staff').filter(staff_id=staff_id)
    for txn in credit_trans:
        combined_data.append({
            'id': txn.id,
            'date': txn.date,
            'amount': txn.amount,
            'note': txn.note,
            'isDebite': False,
            'type': 'Credit',
        })

    processed_dates = set()

    if role == 'weaver':
        pieces = Piece.objects.select_related('warp').filter(warp__weaver_id=staff_id).order_by('-date')

        for piece in pieces:
            piece_date = piece.date
            if piece_date in processed_dates:
                continue

            matching_pieces = Piece.objects.select_related('warp').filter(
                warp__weaver_id=staff_id,
                date=piece_date
            )

            total_amount = 0
            for p in matching_pieces:
                wage = Wage.objects.filter(warp=p.warp.id, date__lte=p.date).order_by('-date', '-id').first()
                if not wage:
                    continue

                if p.type == 'good':
                    rate = wage.wage_good
                    count = p.count
                elif p.type == 'demage':
                    rate = wage.wage_demage
                    count = p.count
                elif p.type == 'extra':
                    rate = wage.wage_extra
                    count = p.count
                else:  # return
                    rate = wage.wage_good
                    count = -p.count

                meter = round(count * (p.length or 0), 2)
                amount = round(rate * meter, 2)
                total_amount += amount

            combined_data.append({
                'date': piece_date,
                'amount': round(total_amount, 2),
                'isDebite': True,
                'type': 'Debit',
            })

            processed_dates.add(piece_date)

    elif role == 'warper':
        warps = Warp.objects.filter(warper_id=staff_id).order_by('-date_start_warper')

        for warp in warps:
            warp_date = warp.date_start_warper
            if not warp_date or warp_date in processed_dates:
                continue

            matching_warps = Warp.objects.filter(warper_id=staff_id, date_start_warper=warp_date)

            total_amount = 0
            for w in matching_warps:
                if w.meters and w.warp_wage:
                    amount = round(w.meters * w.warp_wage, 2)
                    total_amount += amount

            combined_data.append({
                'date': warp_date,
                'amount': round(total_amount, 2),
                'isDebite': True,
                'type': 'Debit',
            })

            processed_dates.add(warp_date)

    combined_data.sort(key=lambda x: x['date'], reverse=True)

    company = get_object_or_404(Company, owner=owner)
    weavers = Staff.objects.filter(company=company).select_related('user')

    return render(request, "core/transactions.html", {
        "combined_data": combined_data,
        "selected_weaver": selected_staff,
        "weavers": weavers,
    })



@login_required
def get_transaction_details(request):
    date_str = request.GET.get('date')
    staff_id = request.GET.get('weaver_id')  # Can be weaver or warper

    date = parse_date(date_str)
    if not date:
        try:
            date = datetime.strptime(date_str, "%B %d, %Y").date()
        except ValueError:
            date = None

    staff = get_object_or_404(CustomUser, id=staff_id)
    role = getattr(staff.staff, 'role', None)

    if role == 'weaver':
        warps = Warp.objects.filter(weaver=staff)
        pieces = Piece.objects.filter(date=date, warp__in=warps)

        for piece in pieces:
            wage = Wage.objects.filter(warp=piece.warp, date__lte=piece.date).order_by('-date', '-id').first()
            if wage:
                if piece.type == 'good':
                    rate = wage.wage_good
                elif piece.type == 'demage':
                    rate = wage.wage_demage
                elif piece.type == 'extra':
                    rate = wage.wage_extra
                else:
                    rate = wage.wage_good
                    piece.count = -piece.count

                piece.meter = round(piece.count * (piece.length or 0), 2)
                piece.amount = round(piece.meter * rate, 2)
            else:
                piece.meter = 0
                piece.amount = 0

        html = render_to_string('core/partial_transaction_popup.html', {
            'role': 'weaver',
            'pieces': pieces,
            'selected_date': date,
        })
        return HttpResponse(html)

    elif role == 'warper':
        warps = Warp.objects.filter(warper=staff, date_start_warper=date)

        total_meters = 0
        total_amount = 0

        for warp in warps:
            warp.amount = round((warp.meters or 0) * (warp.warp_wage or 0), 2)
            total_meters += warp.meters or 0
            total_amount += warp.amount

        html = render_to_string('core/partial_transaction_popup.html', {
            'role': 'warper',
            'warps': warps,
            'selected_date': date,
            'total_meters': total_meters,
            'total_amount': total_amount,
        })
        return HttpResponse(html)

    return HttpResponse("Invalid role", status=400)


@user_passes_test(lambda u: u.is_owner)
def yarn_management(request):
    return render(request, 'core/yarn_management.html')

@user_passes_test(lambda u: u.is_owner)
def create_yarn(request):
    if request.method == 'POST':
        company = get_object_or_404(Company, owner=request.user)
        color = request.POST.get('color')
        color_code = request.POST.get('color_code')
        count = request.POST.get('count')

        Yarn.objects.create(
            company=company,
            color=color,
            count=count,
            color_code=color_code
        )

        messages.success(request, "Yarn created successfully.")
        return redirect('create_yarn')
    return render(request, 'core/create_yarn.html')


@user_passes_test(lambda u: u.is_owner)
def give_yarn(request):
    company = get_object_or_404(Company, owner=request.user)

    yarns = Yarn.objects.filter(company=company)
    staff = Staff.objects.filter(company=company)

    # Get all warps for this company
    warps_qs = Warp.objects.filter(design__company=company).select_related('design')
    warps = list(warps_qs.values('id', 'name', 'weaver_id', 'warper_id', 'warp_yarn', 'meters'))

    # Build warp_entries: yarn requirements for each warp
    warp_entries = {}
    for warp in warps_qs:
        entries = warp.design.entries.select_related('yarn')
        warp_entries[warp.id] = [
            {
                'yarn_id': entry.yarn.id,
                'yarn_name': str(entry.yarn),
                'lint_count': entry.lint_count,
                'color': entry.color
            }
            for entry in entries
        ]

    if request.method == 'POST':
        yarn_id = request.POST.get('yarn_id')
        date = request.POST.get('date')
        quantity = request.POST.get('quantity')
        transaction_type = request.POST.get('transaction_type')
        note = request.POST.get('note', '').strip()
        staff_id = request.POST.get('staff_select')
        staff_obj = None
        to = None

        try:
            yarn = get_object_or_404(Yarn, id=yarn_id, company=company)
            quantity = float(quantity)

            warp_instance = None
            if transaction_type == 'give':
                warp_id = request.POST.get('warp_select')
                if not warp_id:
                    messages.error(request, "Please select a Warp for 'Give' transaction type.")
                    return redirect('give_yarn')
                warp_instance = get_object_or_404(Warp, id=warp_id)

                if staff_id:
                    staff_obj = get_object_or_404(Staff, user__id=staff_id, company=company)
                    to = staff_obj.role

                    if to not in ['weaver', 'warper']:
                        messages.error(request, "Please select a valid 'to' value (weaver/warper).")
                        return redirect('give_yarn')
                else:
                    messages.error(request, "Please select a staff member.")
                    return redirect('give_yarn')

            else:
                warp_instance = None
                to = 'owner'

            Yarn_Transactions.objects.create(
                yarn=yarn,
                date=date,
                quantity=quantity,
                warp=warp_instance,
                transaction_type=transaction_type,
                to=to,
                note=note,
            )

            messages.success(request, "Yarn transaction created successfully.")
            return redirect('warp_wise_yarn_list')

        except (Yarn.DoesNotExist, Warp.DoesNotExist, ValueError) as e:
            messages.error(request, f"Invalid data submitted or missing required selection: {str(e)}")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")


    return render(request, 'core/yarn_transactions.html', {
        'yarns': yarns,
        'staff': staff,
        'warps': warps,
        'warp_entries': warp_entries
    })


@user_passes_test(lambda u: u.is_owner)
def edit_yarn(request, yarn_id):
    company = get_object_or_404(Company, owner=request.user)
    transaction = get_object_or_404(Yarn_Transactions, id=yarn_id, yarn__company=company)

    yarns = Yarn.objects.filter(company=company)
    staff = Staff.objects.filter(company=company)
    warps = Warp.objects.filter(design__company=company).select_related('weaver', 'warper')

    # For JSON script
    warp_data = [
        {
            'id': warp.id,
            'name': warp.name,
            'weaver_id': warp.weaver.id if warp.weaver else None,
            'warper_id': warp.warper.id if warp.warper else None,
        }
        for warp in warps
    ]

    if request.method == 'POST':
        if 'delete_yarn' in request.POST:
            transaction.delete()
            messages.success(request, 'Transaction deleted successfully!')
            return redirect('give_yarn')

        yarn_id = request.POST.get('yarn_id')
        date = request.POST.get('date')
        transaction_type = request.POST.get('transaction_type')
        quantity = request.POST.get('quantity')
        note = request.POST.get('note', '').strip()
        staff_id = request.POST.get('staff_select')

        try:
            yarn = get_object_or_404(Yarn, id=yarn_id, company=company)
            quantity = float(quantity)

            transaction.yarn = yarn
            transaction.date = date
            transaction.transaction_type = transaction_type
            transaction.quantity = quantity
            transaction.note = note

            if transaction_type == 'give':
                if not staff_id:
                    messages.error(request, "Please select a staff member.")
                    return redirect('edit_yarn', yarn_id=transaction.id)

                warp_id = request.POST.get('warp_select')
                if not warp_id:
                    messages.error(request, "Please select a Warp for 'Give' transaction type.")
                    return redirect('edit_yarn', yarn_id=transaction.id)

                warp_instance = get_object_or_404(Warp, id=warp_id, design__company=company)
                staff_obj = get_object_or_404(Staff, user__id=staff_id, company=company)

                if staff_obj.role not in ['weaver', 'warper']:
                    messages.error(request, "Invalid role selected. Must be weaver or warper.")
                    return redirect('edit_yarn', yarn_id=transaction.id)

                transaction.warp = warp_instance
                transaction.to = staff_obj.role

            else:  # buy
                transaction.warp = None
                transaction.to = None

            transaction.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('warp_wise_yarn_list')

        except (Yarn.DoesNotExist, Warp.DoesNotExist, ValueError) as e:
            messages.error(request, f"Invalid data submitted or missing required selection: {str(e)}")
        except Exception as e:
            messages.error(request, f'Error updating transaction: {e}')

    context = {
        'transaction': transaction,
        'yarns': yarns,
        'staff': staff,
        'warps': warps,
        'warp_data': warp_data,
    }
    return render(request, 'core/edit_yarn.html', context)




@user_passes_test(lambda u: u.is_owner)
def yarn_list(request):
    company = get_object_or_404(Company, owner=request.user)
    yarns = Yarn.objects.filter(company=company)

    select_yarn = request.POST.get('staff_yarn') if request.method == 'POST' else None
    yarn_transactions = None

    if select_yarn:
        try:
            selected_yarn_obj = Yarn.objects.get(id=select_yarn, company=company)
            yarn_transactions = Yarn_Transactions.objects.filter(yarn=selected_yarn_obj).select_related('yarn').order_by('-date')
        except Yarn.DoesNotExist:
            selected_yarn_obj = None
            yarn_transactions = None
    else:
        selected_yarn_obj = None
    total = 0
    if yarn_transactions:
        for transaction in yarn_transactions:
            if transaction.transaction_type == 'buy':
                total += transaction.quantity
            elif transaction.transaction_type == 'give':
                total -= transaction.quantity

    context = {
        'select_yarn' : select_yarn,
        'yarns': yarns,
        'select_yarn': selected_yarn_obj,
        'yarn_transactions': yarn_transactions,
        'remaining_quantity': total,
    }

    return render(request, 'core/yarn_list.html', context)





@login_required
def warp_wise_yarn_list(request):
    grouped_yarns = defaultdict(list)
    selected_staff = None
    selected_staff_id = request.GET.get('staff_id')
    company = None

    if hasattr(request.user, 'is_owner') and request.user.is_owner:
        company = get_object_or_404(Company, owner=request.user)
    elif hasattr(request.user, 'is_staff_user') and request.user.is_staff_user:
        company = get_object_or_404(Company, staff__user=request.user)

    if not company:
        messages.error(request, "User is not associated with a company or an owner account.")
        return redirect('home')

    staff_in_company = Staff.objects.filter(company=company).select_related('user').order_by('user__username')

    if request.user.is_authenticated and hasattr(request.user, 'staff') and request.user.staff.company == company:
        selected_staff = request.user
        selected_staff_id = str(request.user.id)
    elif selected_staff_id:
        try:
            selected_staff = CustomUser.objects.get(id=selected_staff_id, staff__company=company)
        except CustomUser.DoesNotExist:
            selected_staff = None
            selected_staff_id = None
            messages.warning(request, "Selected staff not found or not associated with your company.")

    transactions = Yarn_Transactions.objects.none()
    if selected_staff:
        # Determine role of staff
        try:
            role = selected_staff.staff.role  # warper or weaver
        except:
            role = None

        if role in ['weaver', 'warper']:
            warps_for_selected_staff = Warp.objects.filter(**{role: selected_staff})

            transactions = Yarn_Transactions.objects.filter(
                warp__in=warps_for_selected_staff,
                to=role
            ).select_related('yarn', 'warp').order_by('warp__name', 'date')

            for trans in transactions:
                grouped_yarns[trans.warp].append(trans)

    return render(
        request,
        'core/warp_wise_yarn_list.html',
        {
            "grouped_yarns": dict(grouped_yarns),
            "staff_list": staff_in_company,
            "selected_staff": selected_staff,
            "selected_staff_id": selected_staff_id,
            "company": company,
        }
    )
